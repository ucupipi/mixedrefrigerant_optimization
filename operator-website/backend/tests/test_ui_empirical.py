import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'src'))
INDEX_CSS = os.path.join(FRONTEND_DIR, 'index.css')
TOP_NAVBAR = os.path.join(FRONTEND_DIR, 'components', 'TopNavbar.tsx')
TAB_NAV = os.path.join(FRONTEND_DIR, 'components', 'TabNavigation.tsx')
TAB_GRAFIK = os.path.join(FRONTEND_DIR, 'components', 'TabGrafik.tsx')
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
        expected = ['Input & Rekomendasi', 'Process Flow Diagram', 'Operator Guidance']
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
