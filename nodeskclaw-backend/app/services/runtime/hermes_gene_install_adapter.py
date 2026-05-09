"""Hermes-specific gene installation adapter."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.services.runtime.gene_install_adapter import GeneInstallAdapter

if TYPE_CHECKING:
    from app.services.nfs_mount import RemoteFS

logger = logging.getLogger(__name__)


def _normalize_skill_content(content: str) -> str:
    return content.replace("~/.deskclaw/tools", "~/.hermes/scripts")


class HermesGeneInstallAdapter(GeneInstallAdapter):
    def __init__(
        self,
        skills_dir_rel: str = ".hermes/skills",
        scripts_dir_rel: str = ".hermes/scripts",
        snapshot_rel: str = ".hermes/.skills_prompt_snapshot.json",
    ):
        self._skills_dir = skills_dir_rel
        self._scripts_dir = scripts_dir_rel
        self._snapshot_rel = snapshot_rel

    async def deploy_skill(
        self, fs: RemoteFS, skill_name: str, content: str, description: str = "",
    ) -> None:
        content = _normalize_skill_content(content)
        if not content.lstrip().startswith("---"):
            desc = description or f"Skill: {skill_name}"
            content = f"---\nname: {skill_name}\ndescription: {desc}\n---\n\n{content}"

        await fs.mkdir(f"{self._skills_dir}/{skill_name}")
        await fs.write_text(f"{self._skills_dir}/{skill_name}/SKILL.md", content)

    async def allow_tools(self, fs: RemoteFS, tool_names: list[str]) -> None:
        if tool_names:
            logger.debug("HermesGeneInstallAdapter: tool_allow is prompt/skill driven: %s", tool_names)

    async def deploy_scripts(self, fs: RemoteFS, scripts: dict[str, str]) -> None:
        if not scripts:
            return
        await fs.mkdir(self._scripts_dir)
        for filename, content in scripts.items():
            await fs.write_text(f"{self._scripts_dir}/{filename}", content)

    async def apply_config(self, fs: RemoteFS, config_patch: dict) -> None:
        if config_patch:
            logger.debug(
                "HermesGeneInstallAdapter: runtime config patch is not supported yet: %s",
                list(config_patch.keys()),
            )

    async def invalidate_cache(self, fs: RemoteFS, skill_name: str, event: str = "installed") -> None:
        await fs.remove(self._snapshot_rel)

    async def remove_skill(self, fs: RemoteFS, skill_name: str) -> None:
        await fs.remove(f"{self._skills_dir}/{skill_name}")

    async def post_remove_cleanup(self, fs: RemoteFS, skill_name: str) -> None:
        await fs.remove(self._snapshot_rel)
