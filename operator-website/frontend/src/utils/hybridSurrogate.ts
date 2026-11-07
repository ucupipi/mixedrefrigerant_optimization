// Hybrid Surrogate Inference Engine (ONNX Runtime Web with TypeScript Physics Fallback)
// Governance: AGENTS.md (Pasal 1, 2, 5), ORIGINAL_REQUEST.md (R2)
// ZERO em-dash (U+2014) and ZERO en-dash (U+2013) strict rule

import { evaluateRidgeSurrogate } from './physicsEngine';

export interface HybridInferenceStatus {
  model_loaded: boolean;
  engine_mode: 'onnx-web' | 'physics-fallback';
  model_path: string;
  backend: string;
}

export class HybridSurrogateEngine {
  private static instance: HybridSurrogateEngine;
  private session: any = null;
  private isModelLoaded: boolean = false;
  private isInitializing: boolean = false;
  private modelPath: string = '/models/c3mr_power_surrogate.onnx';

  private constructor() {
    // Lazy initialisation on first access in browser environment
    if (typeof window !== 'undefined') {
      this.initSession().catch(() => {
        // Fallback silently to TypeScript physics engine
      });
    }
  }

  public static getInstance(): HybridSurrogateEngine {
    if (!HybridSurrogateEngine.instance) {
      HybridSurrogateEngine.instance = new HybridSurrogateEngine();
    }
    return HybridSurrogateEngine.instance;
  }

  /**
   * Attempt to initialise ONNX Runtime Web session.
   * If onnxruntime-web is not available or model file is absent, gracefully fails.
   */
  public async initSession(): Promise<boolean> {
    if (this.isModelLoaded && this.session) {
      return true;
    }
    if (this.isInitializing) {
      return false;
    }

    this.isInitializing = true;
    try {
      const ort = typeof window !== 'undefined' ? (window as any).ort : null;
      if (!ort || !ort.InferenceSession) {
        this.isModelLoaded = false;
        this.isInitializing = false;
        return false;
      }

      // Configure WASM settings if available
      if (ort.env && ort.env.wasm) {
        ort.env.wasm.numThreads = 1;
        ort.env.wasm.simd = true;
      }

      this.session = await ort.InferenceSession.create(this.modelPath, {
        executionProviders: ['wasm'],
        graphOptimizationLevel: 'all',
      });

      this.isModelLoaded = true;
      this.isInitializing = false;
      return true;
    } catch {
      // Missing ONNX file or unsupported WASM: silently fall back to TypeScript physics
      this.session = null;
      this.isModelLoaded = false;
      this.isInitializing = false;
      return false;
    }
  }

  /**
   * Run surrogate prediction with seamless fallback to pure TypeScript physics engine.
   * Never throws exceptions or displays error dialogues to user.
   */
  public async predict(featureVector: number[]): Promise<number> {
    if (this.isModelLoaded && this.session) {
      try {
        const ort = (window as any).ort;
        const inputName = this.session.inputNames ? this.session.inputNames[0] : 'float_input';
        const tensor = new ort.Tensor('float32', Float32Array.from(featureVector), [1, 20]);
        const feeds: Record<string, any> = {};
        feeds[inputName] = tensor;

        const results = await this.session.run(feeds);
        const outputName = this.session.outputNames ? this.session.outputNames[0] : Object.keys(results)[0];
        const outTensor = results[outputName];

        if (outTensor && outTensor.data && outTensor.data.length > 0) {
          const val = Number(outTensor.data[0]);
          if (Number.isFinite(val)) {
            return val;
          }
        }
      } catch {
        // On any ONNX execution failure, silently delegate to TypeScript physics
      }
    }

    // Pure TypeScript First-Principles Ridge Surrogate Fallback
    return evaluateRidgeSurrogate(featureVector);
  }

  /**
   * Synchronous surrogate evaluation via pure TypeScript physics engine.
   */
  public predictSync(featureVector: number[]): number {
    return evaluateRidgeSurrogate(featureVector);
  }

  public getStatus(): HybridInferenceStatus {
    return {
      model_loaded: this.isModelLoaded,
      engine_mode: this.isModelLoaded ? 'onnx-web' : 'physics-fallback',
      model_path: this.modelPath,
      backend: this.isModelLoaded ? 'ONNX Runtime Web (WASM)' : 'Pure TypeScript First-Principles Physics',
    };
  }

  public isLoaded(): boolean {
    return this.isModelLoaded;
  }
}

export const hybridSurrogate = HybridSurrogateEngine.getInstance();

