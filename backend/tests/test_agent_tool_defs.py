from backend.agent_tool_defs import build_tool_registry
from backend.services.profile_service import ProfileService


def test_build_tool_registry_has_tools():
    registry = build_tool_registry(ProfileService())
    tools = registry.list_tools()

    assert "build_profile" in tools
    assert "extract_axes" in tools
    assert "retrieve_candidates" in tools
    assert "score_candidates" in tools
