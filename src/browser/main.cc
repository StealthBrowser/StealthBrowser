#include "content/public/app/content_main.h"
#include "content/public/app/content_main_runner.h"
#include "content/public/browser/browser_process.h"
#include "content/public/common/main_function_params.h"

#include "base/at_exit.h"
#include "base/command_line.h"
#include "base/logging.h"
#include "base/task/thread_pool/sequence_sort_key.h"

#include "src/browser/browser_process.h"
#include "src/security/security_binding.h"

#if defined(OS_WIN)
#include <windows.h>
#include "content/public/app/sandbox_helper_win.h"
#include "sandbox/win/src/sandbox_types.h"
#endif

namespace {

int RunBrowser(const content::MainFunctionParams& params) {
  LOG(INFO) << "StealthBrowser: Starting browser";

  stealth::BrowserConfig config;
  config.enable_https_only = true;
  config.enable_fingerprint_protection = true;
  config.enable_ad_blocking = true;
  config.clear_data_on_exit = true;

  auto* browser = stealth::BrowserProcess::GetInstance();
  if (!browser->Initialize(config)) {
    LOG(ERROR) << "StealthBrowser: Failed to initialize";
    return 1;
  }

  content::BrowserProcess* bp = content::BrowserProcess::GetInstance();
  if (bp) {
    bp->PostMainTask();
  }

  browser->Shutdown();
  return 0;
}

}  // namespace

#if defined(OS_WIN)
int WINAPI WinMain(HINSTANCE instance, HINSTANCE prev, char* cmdline, int show) {
  sandbox::SandboxInterfaceInfo sandbox_info;
  content::InitializeSandboxInfo(&sandbox_info);

  base::AtExitManager at_exit;
  base::CommandLine::Init(0, nullptr);

  content::MainFunctionParams params;
  params.instance = instance;
  params.sandbox_info = &sandbox_info;

  return RunBrowser(params);
}
#elif defined(OS_POSIX)
int main(int argc, char** argv) {
  base::AtExitManager at_exit;
  base::CommandLine::Init(argc, argv);

  content::MainFunctionParams params;
  params.command_line = base::CommandLine::ForCurrentProcess();

  return RunBrowser(params);
}
#endif
