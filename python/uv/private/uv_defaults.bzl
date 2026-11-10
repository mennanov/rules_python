"""Default `uv` toolchain configuration for WORKSPACE.

Under bzlmod, the equivalent defaults are the `uv.default()` calls in
`MODULE.bazel`. Keep the values here in sync with them.
"""

# <block name="uv-default-version" same-as="MODULE.bazel:uv-default-version" same-as-pattern='"(?P<value>[^"]+)"'>
DEFAULT_VERSION = "0.13.5"
# </block>

# <block name="uv-default-base-url" same-as="MODULE.bazel:uv-default-base-url" same-as-pattern='"(?P<value>[^"]+)"'>
DEFAULT_BASE_URL = "https://github.com/astral-sh/uv/releases/download"
# </block>

def _platform(platform, *, os, cpu):
    # Same shape as the platform structs `set_config` creates.
    return struct(
        name = platform.replace("-", "_").lower(),
        compatible_with = [
            str(Label("@platforms//os:" + os)),
            str(Label("@platforms//cpu:" + cpu)),
        ],
        target_settings = [],
    )

# <block name="uv-platforms" same-as="MODULE.bazel:uv-platforms" same-as-pattern='\("(?P<value>[^"]+)", "'>
DEFAULT_PLATFORMS = {
    platform: _platform(platform, os = os, cpu = cpu)
    for platform, os, cpu in [
        ("aarch64-apple-darwin", "macos", "aarch64"),
        ("aarch64-unknown-linux-gnu", "linux", "aarch64"),
        ("powerpc64le-unknown-linux-gnu", "linux", "ppc64le"),
        ("s390x-unknown-linux-gnu", "linux", "s390x"),
        ("riscv64-unknown-linux-gnu", "linux", "riscv64"),
        ("x86_64-apple-darwin", "macos", "x86_64"),
        ("x86_64-pc-windows-msvc", "windows", "x86_64"),
        ("x86_64-unknown-linux-gnu", "linux", "x86_64"),
    ]
}
# </block>
