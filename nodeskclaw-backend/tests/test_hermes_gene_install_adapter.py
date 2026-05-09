import pytest

from app.services.runtime.hermes_gene_install_adapter import HermesGeneInstallAdapter
from app.services.runtime.registries.runtime_registry import RUNTIME_REGISTRY


class FakeFS:
    def __init__(self):
        self.files = {}
        self.dirs = set()
        self.removed = []

    async def mkdir(self, path: str) -> None:
        self.dirs.add(path)

    async def write_text(self, path: str, content: str) -> None:
        self.files[path] = content

    async def remove(self, path: str) -> None:
        self.removed.append(path)
        self.files.pop(path, None)


@pytest.mark.asyncio
async def test_hermes_gene_adapter_writes_skills_and_scripts_to_hermes_home():
    fs = FakeFS()
    adapter = HermesGeneInstallAdapter()

    await adapter.deploy_skill(fs, "nodeskclaw-shared-files", "Body", "Shared files")
    await adapter.deploy_scripts(fs, {"deskclaw_shared_files.py": "print('ok')"})
    await adapter.invalidate_cache(fs, "nodeskclaw-shared-files")

    assert ".hermes/skills/nodeskclaw-shared-files" in fs.dirs
    assert fs.files[".hermes/skills/nodeskclaw-shared-files/SKILL.md"].startswith("---\n")
    assert fs.files[".hermes/scripts/deskclaw_shared_files.py"] == "print('ok')"
    assert ".hermes/.skills_prompt_snapshot.json" in fs.removed


def test_runtime_registry_uses_hermes_gene_adapter():
    spec = RUNTIME_REGISTRY.get("hermes")

    assert isinstance(spec.gene_install_adapter, HermesGeneInstallAdapter)
