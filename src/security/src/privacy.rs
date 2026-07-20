use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

pub struct PrivacyGuard {
    clear_on_exit: AtomicBool,
    block_cookies: AtomicBool,
    enable_dnt: AtomicBool,
    blocked_requests: AtomicU64,
    stripped_trackers: AtomicU64,
}

impl PrivacyGuard {
    pub fn new() -> Self {
        Self {
            clear_on_exit: AtomicBool::new(true),
            block_cookies: AtomicBool::new(true),
            enable_dnt: AtomicBool::new(true),
            blocked_requests: AtomicU64::new(0),
            stripped_trackers: AtomicU64::new(0),
        }
    }

    pub fn should_clear_on_exit(&self) -> bool {
        self.clear_on_exit.load(Ordering::Relaxed)
    }

    pub fn should_block_cookies(&self) -> bool {
        self.block_cookies.load(Ordering::Relaxed)
    }

    pub fn should_send_dnt(&self) -> bool {
        self.enable_dnt.load(Ordering::Relaxed)
    }

    pub fn record_blocked(&self) {
        self.blocked_requests.fetch_add(1, Ordering::Relaxed);
    }

    pub fn record_stripped_tracker(&self) {
        self.stripped_trackers.fetch_add(1, Ordering::Relaxed);
    }

    pub fn get_blocked_count(&self) -> u64 {
        self.blocked_requests.load(Ordering::Relaxed)
    }

    pub fn get_stripped_count(&self) -> u64 {
        self.stripped_trackers.load(Ordering::Relaxed)
    }

    pub fn set_clear_on_exit(&self, val: bool) {
        self.clear_on_exit.store(val, Ordering::Relaxed);
    }

    pub fn set_block_cookies(&self, val: bool) {
        self.block_cookies.store(val, Ordering::Relaxed);
    }

    pub fn set_enable_dnt(&self, val: bool) {
        self.enable_dnt.store(val, Ordering::Relaxed);
    }

    pub fn clear_session_data(&self) -> Result<(), String> {
        // Clear all in-memory session data
        self.blocked_requests.store(0, Ordering::Relaxed);
        self.stripped_trackers.store(0, Ordering::Relaxed);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    use std::thread;

    #[test]
    fn test_concurrent_access() {
        let guard = Arc::new(PrivacyGuard::new());
        let mut handles = vec![];

        for _ in 0..10 {
            let g = Arc::clone(&guard);
            handles.push(thread::spawn(move || {
                for _ in 0..1000 {
                    g.record_blocked();
                }
            }));
        }

        for h in handles {
            h.join().unwrap();
        }

        assert_eq!(guard.get_blocked_count(), 10000);
    }
}
