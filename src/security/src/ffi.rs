use crate::crypto::CryptoEngine;
use crate::filter::FilterEngine;
use crate::privacy::PrivacyGuard;

pub static mut FILTER_ENGINE: Option<FilterEngine> = None;
pub static mut PRIVACY_GUARD: Option<PrivacyGuard> = None;
pub static mut CRYPTO_ENGINE: Option<CryptoEngine> = None;

#[no_mangle]
pub extern "C" fn stealth_security_init() -> bool {
    let key = CryptoEngine::generate_key();
    unsafe {
        FILTER_ENGINE = Some(FilterEngine::new());
        PRIVACY_GUARD = Some(PrivacyGuard::new());
        CRYPTO_ENGINE = Some(CryptoEngine::new(&key));
    }
    true
}

#[no_mangle]
pub extern "C" fn stealth_should_block_url(url_ptr: *const std::os::raw::c_char) -> bool {
    let url = unsafe {
        if url_ptr.is_null() {
            return false;
        }
        std::ffi::CStr::from_ptr(url_ptr)
            .to_str()
            .unwrap_or("")
    };

    unsafe {
        if let Some(ref engine) = FILTER_ENGINE {
            return engine.should_block(url);
        }
    }
    false
}

#[no_mangle]
pub extern "C" fn stealth_should_upgrade_https(url_ptr: *const std::os::raw::c_char) -> bool {
    let url = unsafe {
        if url_ptr.is_null() {
            return false;
        }
        std::ffi::CStr::from_ptr(url_ptr)
            .to_str()
            .unwrap_or("")
    };

    unsafe {
        if let Some(ref engine) = FILTER_ENGINE {
            return engine.should_upgrade_to_https(url);
        }
    }
    false
}

#[no_mangle]
pub extern "C" fn stealth_get_blocked_count() -> u64 {
    unsafe {
        if let Some(ref guard) = PRIVACY_GUARD {
            return guard.get_blocked_count();
        }
    }
    0
}

#[no_mangle]
pub extern "C" fn stealth_clear_session() -> bool {
    unsafe {
        if let Some(ref guard) = PRIVACY_GUARD {
            return guard.clear_session_data().is_ok();
        }
    }
    false
}

#[no_mangle]
pub extern "C" fn stealth_add_block_domain(domain_ptr: *const std::os::raw::c_char) -> bool {
    let domain = unsafe {
        if domain_ptr.is_null() {
            return false;
        }
        match std::ffi::CStr::from_ptr(domain_ptr).to_str() {
            Ok(s) => s.to_string(),
            Err(_) => return false,
        }
    };

    unsafe {
        if let Some(ref engine) = FILTER_ENGINE {
            engine.add_domain_filter(domain);
            return true;
        }
    }
    false
}

#[no_mangle]
pub extern "C" fn stealth_encrypt_data(
    input_ptr: *const u8,
    input_len: usize,
    output_ptr: *mut u8,
    output_len: *mut usize,
) -> bool {
    let input = unsafe {
        if input_ptr.is_null() || output_ptr.is_null() || output_len.is_null() {
            return false;
        }
        std::slice::from_raw_parts(input_ptr, input_len)
    };

    unsafe {
        if let Some(ref crypto) = CRYPTO_ENGINE {
            match crypto.encrypt(input) {
                Ok(encrypted) => {
                    let bytes = encrypted.as_bytes();
                    let len = bytes.len().min(*output_len);
                    std::ptr::copy_nonoverlapping(bytes.as_ptr(), output_ptr, len);
                    *output_len = len;
                    return true;
                }
                Err(_) => return false,
            }
        }
    }
    false
}

#[no_mangle]
pub extern "C" fn stealth_security_shutdown() {
    unsafe {
        FILTER_ENGINE = None;
        PRIVACY_GUARD = None;
        CRYPTO_ENGINE = None;
    }
}
