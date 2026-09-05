use std::sync::mpsc::{channel, Receiver, Sender};
use std::thread;

pub struct Channel<T> {
    sender: Sender<T>,
    receiver: Receiver<T>,
}

impl<T: Send + 'static> Channel<T> {
    pub fn new() -> Self {
        let (sender, receiver) = channel();
        Self { sender, receiver }
    }

    pub fn send(&self, val: T) -> Result<(), String> {
        self.sender.send(val).map_err(|e| e.to_string())
    }

    pub fn recv(&self) -> Result<T, String> {
        self.receiver.recv().map_err(|e| e.to_string())
    }
}

impl<T: Send + 'static> Default for Channel<T> {
    fn default() -> Self {
        Self::new()
    }
}

pub fn spawn_task<F>(f: F) -> thread::JoinHandle<()>
where
    F: FnOnce() + Send + 'static,
{
    thread::spawn(f)
}
