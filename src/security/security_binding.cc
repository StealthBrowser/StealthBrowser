#include "src/security/security_binding.h"

#include "base/logging.h"

#ifdef STEALTH_HAS_RUST
#include "src/security/rust_bridge.h"
#endif

namespace stealth {

SecurityBinding& SecurityBinding::GetInstance() {
  static SecurityBinding instance;
  return instance;
}

bool SecurityBinding::Initialize() {
#ifdef STEALTH_HAS_RUST
  if (stealth_security_init() != 0) {
    LOG(ERROR) << "StealthSecurity: Failed to initialize Rust security module";
    return false;
  }
  initialized_ = true;
  LOG(INFO) << "StealthSecurity: Rust security module initialized";
  return true;
#else
  LOG(WARNING) << "StealthSecurity: Running without Rust security module";
  initialized_ = true;
  return true;
#endif
}

void SecurityBinding::Shutdown() {
  if (!initialized_) return;

#ifdef STEALTH_HAS_RUST
  stealth_security_shutdown();
#endif
  initialized_ = false;
  LOG(INFO) << "StealthSecurity: Shutdown complete";
}

bool SecurityBinding::ShouldBlockURL(const std::string& url) const {
#ifdef STEALTH_HAS_RUST
  return stealth_should_block_url(url.c_str()) != 0;
#else
  return false;
#endif
}

bool SecurityBinding::ShouldUpgradeHTTPS(const std::string& url) const {
#ifdef STEALTH_HAS_RUST
  return stealth_should_upgrade_https(url.c_str()) != 0;
#else
  return url.find("http://") == 0;
#endif
}

uint64_t SecurityBinding::GetBlockedCount() const {
#ifdef STEALTH_HAS_RUST
  return stealth_get_blocked_count();
#else
  return 0;
#endif
}

void SecurityBinding::ClearSession() {
#ifdef STEALTH_HAS_RUST
  stealth_clear_session();
#endif
}

bool SecurityBinding::AddBlockDomain(const std::string& domain) {
#ifdef STEALTH_HAS_RUST
  return stealth_add_block_domain(domain.c_str()) != 0;
#else
  return false;
#endif
}

}  // namespace stealth
