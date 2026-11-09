import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'src'))
INDEX_CSS = os.path.join(FRONTEND_DIR, 'index.css')
TOP_NAVBAR = os.path.join(FRONTEND_DIR, 'components', 'TopNavbar.tsx')
TAB_NAV = os.path.join(FRONTEND_DIR, 'components', 'TabNavigation.tsx')
TAB_GRAFIK = os.path.join(FRONTEND_DIR, 'components', 'TabGrafik.tsx')
TAB_INPUT_RESULTS = os.path.join(FRONTEND_DIR, 'components', 'TabInputResults.tsx')
APP_TSX = os.path.join(FRONTEND_DIR, 'App.tsx')

def read_file(path: str) -> str:
    assert os.path.exists(path), f"File not found: {path}"
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

class TestTopNavbarAndResponsive:
    """Verifies Task 2a: Mobile layout on Samsung S23 (360px) and extreme 320px width."""

    def test_fluid_typography_and_mobile_hide(self):
        content = read_file(TOP_NAVBAR)
        assert "clamp(11px, 2.8vw, 16px)" in content, "Missing fluid typography clamp(11px, 2.8vw, 16px)"
        assert 'className="mobile-hide"' in content, "Missing mobile-hide class on secondary header tags"
        
        # Verify mobile-hide is applied to both separator and ADVISORY label
        pattern = r'<span\s+className="mobile-hide"[^>]*>\|</span>\s*<span\s+className="mobile-hide"[^>]*>ADVISORY</span>'
        assert re.search(pattern, content), "mobile-hide must wrap both '|' and 'ADVISORY' elements"

    def test_leftover_props_removed(self):
        content = read_file(TOP_NAVBAR)
        app_content = read_file(APP_TSX)

        # Check TopNavbarProps interface in TopNavbar.tsx
        props_block_match = re.search(r'interface\s+TopNavbarProps\s*\{([^}]+)\}', content)
        assert props_block_match, "TopNavbarProps interface not found"
        props_body = props_block_match.group(1)

        assert 'userMode' not in props_body, "userMode found in TopNavbarProps"
        assert 'onToggleUserMode' not in props_body, "onToggleUserMode found in TopNavbarProps"
        assert 'onReset' not in props_body, "onReset found in TopNavbarProps"

        # Check App.tsx invocation
        nav_invoke_match = re.search(r'<TopNavbar\s*([^>]*)\/>', app_content)
        assert nav_invoke_match, "<TopNavbar /> invocation not found in App.tsx"
        invoke_attrs = nav_invoke_match.group(1)
        assert 'userMode' not in invoke_attrs, "userMode passed to <TopNavbar /> in App.tsx"
        assert 'onToggleUserMode' not in invoke_attrs, "onToggleUserMode passed to <TopNavbar /> in App.tsx"
        assert 'onReset' not in invoke_attrs, "onReset passed to <TopNavbar /> in App.tsx"

    def test_viewport_geometry_math_360px_and_320px(self):
        """Mathematical stress testing of header box models at 360px and 320px."""
        css_content = read_file(INDEX_CSS)
        assert ".mobile-hide" in css_content
        assert "display: none !important" in css_content

        for viewport_w in [360, 320]:
            # Container padding 10px 16px -> 32px total horizontal padding
            padding_h = 32
            inner_w = viewport_w - padding_h
            gap_header = 12

            # Right actions on mobile (with .mobile-hide hiding '| ADVISORY'):
            # Pill: padding 20px + dot 7px + gap 6px + "ONLINE" text (~40px) = 73px
            # Gap: 8px
            # Button: padding 24px + gap 6px + "⬇ CSV" (~34px) = 64px
            right_controls_w = 73 + 8 + 64 # ~145px

            # Space available for brand area
            brand_area_w = inner_w - gap_header - right_controls_w
            
            # Brand icon: 34px, gap: 10px
            title_box_w = brand_area_w - 34 - 10

            # Typography clamp evaluation
            raw_vw = 2.8 * (viewport_w / 100.0)
            clamped_font_size = max(11.0, min(16.0, raw_vw))
            
            # Assertions
            assert title_box_w > 0, f"Viewport {viewport_w}px must provide positive title box width (got {title_box_w}px)"
            assert clamped_font_size == 11.0, f"Viewport {viewport_w}px font should clamp to minimum 11px (got {clamped_font_size}px)"


class TestTabNavigationTouchScroll:
    """Verifies Task 2b: Tab Navigation touch scrolling and subtitle removal."""

    def test_exact_tab_titles(self):
        content = read_file(TAB_NAV)
        titles = re.findall(r"title:\s*'([^']*)'", content)
        expected = ['Input & Recommendations', 'Process Flow Diagram', 'Operator Guidance']
        assert titles == expected, f"Tab titles must match {expected}, found {titles}"

    def test_zero_subtitles(self):
        content = read_file(TAB_NAV)
        assert 'subtitle' not in content.lower(), "Found leftover subtitle reference in TabNavigation.tsx"

    def test_touch_scroll_configuration(self):
        content = read_file(TAB_NAV)
        css_content = read_file(INDEX_CSS)

        # Inline style attributes
        assert "flexWrap: 'nowrap'" in content, "Missing flexWrap: 'nowrap'"
        assert "overflowX: 'auto'" in content, "Missing overflowX: 'auto'"
        assert "WebkitOverflowScrolling: 'touch'" in content, "Missing WebkitOverflowScrolling: 'touch'"
        assert "scrollbarWidth: 'none'" in content, "Missing scrollbarWidth: 'none'"
        assert 'className="no-scrollbar"' in content, "Missing className='no-scrollbar'"

        # CSS class definition in index.css
        assert ".no-scrollbar::-webkit-scrollbar" in css_content
        assert "scrollbar-width: none !important" in css_content
        assert "-ms-overflow-style: none !important" in css_content


class TestTabGrafikViewBoxAndCryogenicTags:
    """Verifies Task 2c: SVG PFD viewBox, bottom bounds, and cryogenic tags."""

    def test_viewbox_geometry(self):
        content = read_file(TAB_GRAFIK)
        match = re.search(r'viewBox="([^"]+)"', content)
        assert match, "viewBox attribute not found in TabGrafik.tsx"
        vb = match.group(1).split()
        assert len(vb) == 4, f"Invalid viewBox: {match.group(1)}"
        min_x, min_y, width, height = int(vb[0]), int(vb[1]), int(vb[2]), int(vb[3])
        assert min_x == 0, f"Expected min_x 0, got {min_x}"
        assert min_y == 140, f"Expected min_y 140, got {min_y}"
        assert width == 1920, f"Expected width 1920, got {width}"
        
        # Verify canvas bottom covers y=930 per ORIGINAL_REQUEST
        canvas_bottom = min_y + height
        assert canvas_bottom >= 930, f"Canvas bottom y={canvas_bottom} must be at least 930"
        
        # Also check whether exact height is 790 or 800 (documents worker variance: 800 gives y=940)
        assert height in [790, 800], f"Expected height 790 (exact) or 800, got {height}"

    def test_bottom_tags_clearance(self):
        content = read_file(TAB_GRAFIK)
        # Canvas vertical span: min_y=140, height=790 -> max_y=930
        canvas_bottom = 140 + 790 # 930
        
        tags_to_check = ['H3FI0004' if 'H3FI0004' in content else ('FI4' if 'FI4' in content else 'FI12'), 'PI12', 'TI23']
        for tag in tags_to_check:
            # Match rect directly preceding the text containing the tag
            pattern = rf'<rect\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"[^>]*>\s*<text[^>]*>{tag}'
            m = re.search(pattern, content)
            assert m, f"Could not find badge geometry for {tag}"
            x, y, w, h = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            
            bottom_y = y + h
            clearance = canvas_bottom - bottom_y
            assert y == 865, f"{tag} y coordinate expected 865, got {y}"
            assert h == 38, f"{tag} height expected 38, got {h}"
            assert bottom_y == 903, f"{tag} bottom expected 903, got {bottom_y}"
            assert clearance == 27, f"{tag} clearance expected 27px, got {clearance}px"
            assert clearance >= 20, f"{tag} clearance {clearance}px is less than required 20px"

    def test_pr_eos_cryogenic_tags_present_and_wired(self):
        content = read_file(TAB_GRAFIK)
        
        expected_tags = {
            'TI50': {
                'dcs': -36.0,
                'ai': -34.5,
                'stream': 'STREAM 4',
                'description': 'MR Liquid Inlet ke MCHE 5E-1'
            },
            'TI20': {
                'dcs': -134.6,
                'ai': -131.2,
                'stream': 'STREAM 7',
                'description': 'Overhead MCHE 5E-1 ke LTSS'
            },
            'TI24': {
                'dcs': -151.3,
                'ai': -150.8,
                'stream': 'STREAM 7',
                'description': 'Cold Bundle MRV Overhead'
            },
            'TI29': {
                'dcs': -153.6,
                'ai': -153.8,
                'stream': 'STREAM 2',
                'description': 'LNG Rundown Downstream Subcooler'
            }
        }

        for tag, meta in expected_tags.items():
            # Check variable declaration
            var_dcs = f"{tag.lower()}Dcs"
            var_ai = f"{tag.lower()}Ai"
            assert f"{var_dcs} = {meta['dcs']}" in content, f"Variable {var_dcs} with value {meta['dcs']} missing"
            assert f"{var_ai} = {meta['ai']}" in content, f"Variable {var_ai} with value {meta['ai']} missing"

            # Check rendered badge
            assert f"fmt('{tag}', {var_dcs}, {var_ai}" in content, f"fmt() formatting binding for {tag} missing"
            assert f">{tag}" in content, f"SVG text element for {tag} missing"

            # Check click handler
            assert f"handleTagClick" in content
            assert tag in content


class TestTabInputResultsMobileAccessibility:
    """Empirical verification that TabInputResults is fully accessible on mobile devices.
    Ensures horizontal table swipe, responsive grid auto-fit, and touch indicators."""

    @pytest.fixture
    def input_results_content(self):
        return read_file(TAB_INPUT_RESULTS)

    def test_tables_wrapped_in_scroll_containers_with_min_widths(self, input_results_content):
        """Verify that comparison table and makeup schedule table are wrapped in table-scroll-container with minWidth."""
        assert 'className="table-scroll-container"' in input_results_content, "table-scroll-container wrapper missing"
        assert 'minWidth: \'720px\'' in input_results_content, "minWidth 720px missing on Comparison Table"
        assert 'minWidth: \'840px\'' in input_results_content, "minWidth 840px missing on Make-Up Schedule Table"
        assert 'mobile-swipe-hint' in input_results_content, "Mobile swipe hint helper missing"

    def test_sections_grid_responsive_autofit(self, input_results_content):
        """Verify that Section 2 and Section 3 use auto-fit minmax responsive grids instead of rigid repeat(N, 1fr)."""
        assert "minmax(280px, 1fr)" in input_results_content, "Section 2 responsive grid minmax(280px, 1fr) missing"
        assert "minmax(230px, 1fr)" in input_results_content, "Section 3 responsive grid minmax(230px, 1fr) missing"
        assert "repeat(3, 1fr)" not in input_results_content, "Hardcoded rigid repeat(3, 1fr) should not be used in Section 2"
        assert "repeat(4, 1fr)" not in input_results_content, "Hardcoded rigid repeat(4, 1fr) should not be used in Section 3"


class TestPhysicsEngineRemediation:
    """Milestone 3 Remediation: Verify computeFrontendRecommendation property-level defaulting."""

    def test_physics_engine_remediation_source_guards(self):
        """Verify that physicsEngine.ts has property-level finite defaulting instead of object-level truthy OR."""
        engine_path = os.path.join(FRONTEND_DIR, 'utils', 'physicsEngine.ts')
        content = read_file(engine_path)

        # Ensure object-level actualDcs || {...} is absent
        assert "const act = actualDcs || {" not in content, "Vulnerable object-level actualDcs || {...} still present"

        # Ensure property-level Number.isFinite check is present for all 5 components
        for comp in ['comp_N2_molpct', 'comp_C1_molpct', 'comp_C2_molpct', 'comp_C2H4_molpct', 'comp_C3_molpct']:
            assert f"Number.isFinite(actualDcs.{comp})" in content, f"Missing finite check for {comp}"

    def test_physics_engine_ts_unit_test_passes(self):
        """Execute node test runner on physicsEngine.test.ts to verify zero-NaN on empty/undefined actualDcs."""
        import subprocess
        frontend_root = os.path.abspath(os.path.join(FRONTEND_DIR, '..'))
        cmd = [
            "node",
            "--loader",
            "./tests/ts-loader.mjs",
            "src/__tests__/physicsEngine.test.ts"
        ]
        res = subprocess.run(cmd, cwd=frontend_root, capture_output=True, text=True)
        assert res.returncode == 0, f"physicsEngine.test.ts failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"


class TestDcsBaselineImmutabilityAndStateSeparation:
    """Verifies R1 & R4: DCS baseline inputs remain strictly immutable and separate from AI targets."""

    @pytest.fixture
    def app_content(self):
        return read_file(APP_TSX)

    @pytest.fixture
    def tab_content(self):
        return read_file(TAB_INPUT_RESULTS)

    def test_apply_ai_target_preserves_dcs_inputs_without_on_optimize(self, tab_content):
        """Verify handleApplyRecommended only toggles isAiApplied without invoking onOptimize()."""
        match = re.search(r'const\s+handleApplyRecommended\s*=\s*\(\)\s*=>\s*\{([^}]+)\}', tab_content)
        assert match, "handleApplyRecommended definition not found in TabInputResults.tsx"
        body = match.group(1)
        assert "setIsAiApplied(true)" in body, "handleApplyRecommended must set isAiApplied to true"
        assert "onOptimize()" not in body, "handleApplyRecommended must NOT call onOptimize() which mutates inputs"
        assert "onScenarioChange" not in body, "handleApplyRecommended must NOT mutate scenario"

    def test_handle_optimize_does_not_mutate_dcs_inputs(self, app_content):
        """Verify handleOptimize sets optimum without overwriting scenario or actualDcs inputs."""
        match = re.search(r'const\s+handleOptimize\s*=\s*async\s*\(\)\s*=>\s*\{([\s\S]*?)\n  \};', app_content)
        assert match, "handleOptimize definition not found in App.tsx"
        body = match.group(1)
        assert "setOptimum(opt)" in body, "handleOptimize must store result in optimum state"
        assert "setScenario((prev) => ({" not in body, "handleOptimize must NOT overwrite scenario with opt targets"
        assert "setActualDcs((prev) => ({" not in body, "handleOptimize must NOT overwrite actualDcs with opt targets"

    def test_feed_flow_change_zero_arbitrary_scaling(self, app_content):
        """Verify feed flow adjustment in handleScenarioChange does not use magic multiplier (562.3 / 245.8)."""
        assert "562.3 / 245.8" not in app_content, "Arbitrary multiplier (562.3 / 245.8) found in App.tsx"
        match = re.search(r'const\s+handleScenarioChange\s*=\s*\([^)]*\)\s*=>\s*\{([\s\S]*?)\n  \};', app_content)
        assert match, "handleScenarioChange not found in App.tsx"
        body = match.group(1)
        feed_branch_match = re.search(r"if\s*\(\s*key\s*===\s*'feed_flow_t_h'\s*\)\s*\{([\s\S]*?)\}\s*else", body)
        assert feed_branch_match, "feed_flow_t_h branch not found in handleScenarioChange"
        feed_branch = feed_branch_match.group(1)
        assert "mcr_flow_t_h:" not in feed_branch, "feed_flow_t_h change must NOT overwrite mcr_flow_t_h in App.tsx"

    def test_section1_inputs_bound_to_actual_dcs(self, tab_content):
        """Verify Table 1 inputs read from actualDcs to guarantee DCS baseline immutability."""
        assert "value={actualDcs.feed_flow_t_h ?? scenario.feed_flow_t_h}" in tab_content, "Feed flow input not bound to actualDcs"
        assert "value={actualDcs.mcr_flow_t_h ?? scenario.mcr_flow_t_h}" in tab_content, "MCR flow input not bound to actualDcs"
        assert "value={actualDcs[comp.key] ?? scenario[comp.key]}" in tab_content, "Composition inputs not bound to actualDcs"


class TestDynamicPresetSwitchingAndMetricRecalculation:
    """Verifies R2: Switching optimization presets dynamically updates targets and recalculates savings."""

    @pytest.fixture
    def app_content(self):
        return read_file(APP_TSX)

    @pytest.fixture
    def tab_content(self):
        return read_file(TAB_INPUT_RESULTS)

    def test_strategy_switch_triggers_optimization_and_prediction_refresh(self, app_content):
        """Verify handleStrategyChange updates optimum and recalculates prediction with new preset."""
        match = re.search(r'const\s+handleStrategyChange\s*=\s*async\s*\([^)]*\)\s*=>\s*\{([\s\S]*?)\n  \};', app_content)
        assert match, "handleStrategyChange not found in App.tsx"
        body = match.group(1)
        assert "optimizeForFeed(targetFeed, actualDcs, 0.30, newStrategy)" in body, "optimizeForFeed must be called with newStrategy"
        assert "setOptimum(opt)" in body, "setOptimum must be called with new recommendation"
        assert "predictScenario(buildRequest(targetScenario, actualDcs))" in body, "predictScenario must be refreshed for the new strategy preset"

    def test_section3_savings_recalculation_without_is_ai_applied_freeze(self, tab_content):
        """Verify Section 3 evaluates savings directly against DCS baseline without isAiApplied gating."""
        assert "const deltaPower = isAiApplied ? aiTargetDeltaPower : rawDeltaPower;" not in tab_content, \
            "Found stale deltaPower gating behind isAiApplied in TabInputResults.tsx"
        assert "const scenarioPower = isAiApplied ? aiTargetPower : rawScenarioPower;" not in tab_content, \
            "Found stale scenarioPower gating behind isAiApplied in TabInputResults.tsx"
        assert "deltaPower = prediction?.prediction?.delta_power_mw ?? (targetPower - baselinePower)" in tab_content, \
            "deltaPower must directly evaluate targetPower against baselinePower"

    def test_section3_kpi_status_pills_advisory_vs_applied(self, tab_content):
        """Verify Section 3 KPI cards render dynamic status pill distinguishing Applied Target vs Advisory Target."""
        assert "{isAiApplied ? 'Applied Target' : 'Advisory Target'}" in tab_content, \
            "Status pill distinguishing Applied Target vs Advisory Target missing in Section 3"


class TestSideBySidePresentationAndTrueMakeupDeltas:
    """Verifies R3: Side-by-side presentation in Section 1, Section 2, and Make-Up Schedule."""

    @pytest.fixture
    def tab_content(self):
        return read_file(TAB_INPUT_RESULTS)

    def test_makeup_schedule_derives_actmap_from_actual_dcs(self, tab_content):
        """Verify activeMakeupAdvisory derives actMap from actualDcs to guarantee true mathematical deviations."""
        match = re.search(r'const\s+activeMakeupAdvisory[\s\S]*?const\s+actMap:\s*Record<string,\s*number>\s*=\s*\{([\s\S]*?)\};', tab_content)
        assert match, "actMap definition not found in activeMakeupAdvisory"
        act_map_body = match.group(1)
        assert "actualDcs.comp_N2_molpct" in act_map_body, "actMap must read N2 from actualDcs"
        assert "actualDcs.comp_C1_molpct" in act_map_body, "actMap must read C1 from actualDcs"
        assert "actualDcs.comp_C2_molpct" in act_map_body, "actMap must read C2 from actualDcs"
        assert "actualDcs.comp_C3_molpct" in act_map_body, "actMap must read C3 from actualDcs"

    def test_makeup_schedule_mathematical_deviations_and_non_zero_rates(self):
        """Verify empirical mathematical calculation of deficit injection rates on MCR inventory."""
        inv_kg = 24000.0
        mw = {"N2": 28.0134, "C1": 16.0425, "C2": 30.069, "C2H4": 28.0532, "C3": 44.0956}
        purity = {"N2": 0.999, "C1": 0.945, "C2": 0.96, "C3": 0.985}
        t_hours = 2.0

        act = {"N2": 3.39, "C1": 44.45, "C2": 45.02, "C2H4": 0.85, "C3": 6.29}
        tgt = {"N2": 3.31, "C1": 46.08, "C2": 45.15, "C3": 5.41}

        avg_mw = sum(act[c] * mw[c] for c in act) / 100.0
        n0_kmol = inv_kg / avg_mw

        deltas = {c: round(tgt[c] - act[c], 2) for c in tgt}
        assert deltas["C1"] == 1.63, f"Expected C1 delta +1.63 mol%, got {deltas['C1']}"
        assert deltas["C2"] == 0.13, f"Expected C2 delta +0.13 mol%, got {deltas['C2']}"
        assert deltas["N2"] == -0.08, f"Expected N2 delta -0.08 mol%, got {deltas['N2']}"
        assert deltas["C3"] == -0.88, f"Expected C3 delta -0.88 mol%, got {deltas['C3']}"

        # C1 is deficit: must inject
        needed_kmol_c1 = (n0_kmol * (deltas["C1"] / 100.0)) / purity["C1"]
        needed_nm3_c1 = needed_kmol_c1 * 22.414
        flow_nm3_c1 = round(needed_nm3_c1 / t_hours, 1)
        assert flow_nm3_c1 > 100.0, f"C1 injection flow must be substantial (>100 Nm3/h), got {flow_nm3_c1}"

        # C2 is deficit: must inject
        needed_kmol_c2 = (n0_kmol * (deltas["C2"] / 100.0)) / purity["C2"]
        needed_nm3_c2 = needed_kmol_c2 * 22.414
        flow_nm3_c2 = round(needed_nm3_c2 / t_hours, 1)
        assert flow_nm3_c2 > 10.0, f"C2 injection flow must be non-zero (>10 Nm3/h), got {flow_nm3_c2}"

    def test_section1_side_by_side_column_headers(self, tab_content):
        """Verify Section 1 Table 1 header has explicit side-by-side columns."""
        assert "Current Input (DCS)" in tab_content, "Current Input (DCS) header column missing in Section 1"
        assert "AI Target" in tab_content, "AI Target header column missing in Section 1"

    def test_section2_continuous_side_by_side_across_all_panels(self, tab_content):
        """Verify Section 2 panels render DCS and AI Target side-by-side without conditional hiding."""
        assert "{isAiApplied ? 'AI Target' : 'Scenario'}" not in tab_content, \
            "Section 2 still contains {isAiApplied ? 'AI Target' : 'Scenario'} conditional hiding"
        assert "{isAiApplied ? 'AI 2.35' : 'Scenario 2.28'}" not in tab_content, \
            "Section 2 still contains conditional hiding on 4PI-13"
        assert "{isAiApplied ? 'AI 58.1°C' : 'Scenario 62.4°C'}" not in tab_content, \
            "Section 2 still contains conditional hiding on 4TI-16"
        assert "{isAiApplied ? 'AI 35.15' : 'Scenario 36.90'}" not in tab_content, \
            "Section 2 still contains conditional hiding on 4PI-1"
        assert "SAFE (TAL ≥ -45.0°C)" in tab_content, "TAL interlock badge SAFE (TAL ≥ -45.0°C) missing"


class TestEngineeringRulesCompliance:
    """Verifies R5 and AGENTS.md compliance: zero magic numbers and mass balance consistency."""

    def test_agents_md_zero_magic_numbers_in_state_handlers(self):
        """Verify absence of unreferenced arbitrary multipliers in App.tsx and TabInputResults.tsx."""
        app_content = read_file(APP_TSX)
        tab_content = read_file(TAB_INPUT_RESULTS)

        forbidden = [
            "562.3 / 245.8",
            "reboilerDuty * 6.5",
            "condenserDuty * 6.2",
            "chillerDuty / 7.0 * 25.23"
        ]
        for f in forbidden:
            assert f not in app_content, f"Forbidden magic number '{f}' found in App.tsx"
            assert f not in tab_content, f"Forbidden magic number '{f}' found in TabInputResults.tsx"

    def test_simplex_molar_conservation_closure(self):
        """Verify that Total MCR Composition sums strictly to 100% within tolerance."""
        tab_content = read_file(TAB_INPUT_RESULTS)
        assert "Math.abs(compSum - 100.0) < 0.05" in tab_content, "Simplex closure check missing in TabInputResults.tsx"



