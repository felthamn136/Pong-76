use crate::game::SoundEvent;
use rodio::{source::SineWave, OutputStream, OutputStreamHandle, Sink, Source};
use std::time::Duration;

pub struct Audio {
    _stream: OutputStream,
    stream_handle: OutputStreamHandle,
}

impl Audio {
    pub fn new() -> Result<Self, String> {
        let (_stream, stream_handle) =
            OutputStream::try_default().map_err(|error| error.to_string())?;
        Ok(Self {
            _stream,
            stream_handle,
        })
    }

    pub fn play(&self, event: SoundEvent) -> Result<(), String> {
        let (frequency, duration) = match event {
            SoundEvent::PaddleHit => (480.0, Duration::from_millis(50)),
            SoundEvent::WallBounce => (240.0, Duration::from_millis(50)),
            SoundEvent::ScorePoint => (240.0, Duration::from_millis(250)),
        };
        let sink = Sink::try_new(&self.stream_handle).map_err(|error| error.to_string())?;
        sink.append(
            SineWave::new(frequency)
                .take_duration(duration)
                .amplify(0.15),
        );
        sink.detach();
        Ok(())
    }
}
