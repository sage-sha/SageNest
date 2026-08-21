use std::sync::{Arc, Mutex};

use serde::Serialize;

#[derive(Clone, Serialize)]
pub struct Deployment {
    pub commit: String,
    pub branch: String,
    pub image_tag: String,
    pub container_id: String,
    pub url: String,
}

#[derive(Clone, Default)]
pub struct AppState {
    deployment: Arc<Mutex<Option<Deployment>>>,
}

impl AppState {
    pub fn current(&self) -> Option<Deployment> {
        self.deployment.lock().expect("state lock").clone()
    }

    pub fn swap(&self, next: Deployment) -> Option<Deployment> {
        self.deployment.lock().expect("state lock").replace(next)
    }
}
