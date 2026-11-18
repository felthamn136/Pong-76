use rand::Rng;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PaddleSize {
    Small,
    Large,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Controls {
    Keyboard,
    Joystick,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GameColour {
    White,
    Green,
    Amber,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SoundEvent {
    PaddleHit,
    WallBounce,
    ScorePoint,
}

impl GameColour {
    pub fn rgb(self) -> (u8, u8, u8) {
        match self {
            Self::White => (244, 244, 244),
            Self::Green => (125, 255, 122),
            Self::Amber => (244, 232, 193),
        }
    }
}

#[derive(Clone, Debug)]
pub struct Settings {
    pub players: usize,
    pub paddle_size: PaddleSize,
    pub angle_degrees: f32,
    pub fast: bool,
    pub scanlines: bool,
    pub controls: Controls,
    pub colour: GameColour,
    pub autoserve: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            players: 1,
            paddle_size: PaddleSize::Small,
            angle_degrees: 20.0,
            fast: false,
            scanlines: true,
            controls: Controls::Keyboard,
            colour: GameColour::White,
            autoserve: false,
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Court {
    pub top: f32,
    pub bottom: f32,
    pub left_x: f32,
    pub right_x: f32,
    pub paddle_width: f32,
    pub paddle_height: f32,
    pub ball_radius: f32,
    pub paddle_speed: f32,
}

impl Court {
    pub fn new(width: f32, height: f32, settings: &Settings) -> Self {
        let scale = ((width / 800.0) * (height / 600.0)).sqrt();
        let paddle_width = 10.0 * scale;
        Self {
            top: height * 0.14,
            bottom: height * 0.9,
            left_x: width * 0.07,
            right_x: width - width * 0.07 - paddle_width,
            paddle_width,
            paddle_height: (if settings.paddle_size == PaddleSize::Small {
                72.0
            } else {
                110.0
            }) * scale,
            ball_radius: 6.0 * scale,
            paddle_speed: 420.0 * height / 600.0,
        }
    }
}

pub struct Game {
    pub width: f32,
    pub height: f32,
    pub left_y: f32,
    pub right_y: f32,
    pub ball_x: f32,
    pub ball_y: f32,
    pub ball_vx: f32,
    pub ball_vy: f32,
    pub left_score: u32,
    pub right_score: u32,
    pub game_over: bool,
    paused: bool,
    pub winner: String,
    waiting_to_serve: bool,
    serve_direction: f32,
    serve_remaining: f32,
    ball_speed: f32,
}

impl Game {
    pub fn new(settings: &Settings, width: f32, height: f32) -> Self {
        let width = width.max(1.0);
        let height = height.max(1.0);
        let mut game = Self {
            width,
            height,
            left_y: height / 2.0,
            right_y: height / 2.0,
            ball_x: width / 2.0,
            ball_y: height / 2.0,
            ball_vx: 0.0,
            ball_vy: 0.0,
            left_score: 0,
            right_score: 0,
            game_over: false,
            paused: false,
            winner: String::new(),
            waiting_to_serve: false,
            serve_direction: 1.0,
            serve_remaining: 0.0,
            ball_speed: (if settings.fast { 500.0 } else { 330.0 }) * width / 800.0,
        };
        game.reset_ball(settings, None);
        game
    }

    pub fn waiting_to_serve(&self) -> bool {
        self.waiting_to_serve
    }

    pub fn is_paused(&self) -> bool {
        self.paused
    }

    pub fn toggle_pause(&mut self) {
        if !self.game_over {
            self.paused = !self.paused;
        }
    }

    pub fn serve(&mut self, settings: &Settings) {
        if self.waiting_to_serve && !self.game_over {
            self.launch_ball(settings);
        }
    }

    pub fn resize(&mut self, width: f32, height: f32) {
        let width = width.max(1.0);
        let height = height.max(1.0);
        if self.width == width && self.height == height {
            return;
        }
        self.ball_x *= width / self.width;
        self.ball_y *= height / self.height;
        self.left_y *= height / self.height;
        self.right_y *= height / self.height;
        self.ball_vx *= width / self.width;
        self.ball_vy *= height / self.height;
        self.width = width;
        self.height = height;
    }

    pub fn reset_match(&mut self, settings: &Settings) {
        self.left_score = 0;
        self.right_score = 0;
        self.game_over = false;
        self.paused = false;
        self.winner.clear();
        self.reset_ball(settings, None);
    }

    pub fn tick(
        &mut self,
        settings: &Settings,
        dt: f32,
        left_input: f32,
        right_input: f32,
    ) -> Vec<SoundEvent> {
        let mut sound_events = Vec::new();
        if self.game_over || self.paused {
            return sound_events;
        }
        let dt = dt.clamp(0.0, 0.05);
        let court = Court::new(self.width, self.height, settings);
        let half_paddle = court.paddle_height / 2.0;
        self.left_y = move_paddle(
            self.left_y,
            left_input,
            court.paddle_speed,
            dt,
            court,
            half_paddle,
        );

        if settings.players == 2 {
            self.right_y = move_paddle(
                self.right_y,
                right_input,
                court.paddle_speed,
                dt,
                court,
                half_paddle,
            );
        } else {
            let target_y = if self.ball_vx > 0.0 {
                self.ball_y
            } else {
                self.height / 2.0
            };
            let difference = target_y - self.right_y;
            let direction = if difference > 0.0 { 1.0 } else { -1.0 };
            let step = difference.abs().min(court.paddle_speed * 0.78 * dt);
            self.right_y += direction * step;
        }

        if self.waiting_to_serve {
            return sound_events;
        }
        if self.serve_remaining > 0.0 {
            self.serve_remaining = (self.serve_remaining - dt).max(0.0);
            return sound_events;
        }

        self.ball_x += self.ball_vx * dt;
        self.ball_y += self.ball_vy * dt;
        let radius = court.ball_radius;
        if self.ball_y - radius < court.top {
            self.ball_y = court.top + radius;
            self.ball_vy = self.ball_vy.abs();
            sound_events.push(SoundEvent::WallBounce);
        } else if self.ball_y + radius > court.bottom {
            self.ball_y = court.bottom - radius;
            self.ball_vy = -self.ball_vy.abs();
            sound_events.push(SoundEvent::WallBounce);
        }

        let left_face = court.left_x + court.paddle_width;
        if self.ball_vx < 0.0
            && self.ball_x - radius <= left_face
            && self.ball_x + radius >= court.left_x
            && (self.ball_y - self.left_y).abs() <= half_paddle + radius
        {
            self.ball_x = left_face + radius;
            self.bounce_from_paddle(1.0, self.left_y, half_paddle, settings);
            sound_events.push(SoundEvent::PaddleHit);
        } else if self.ball_vx > 0.0
            && self.ball_x + radius >= court.right_x
            && self.ball_x - radius <= court.right_x + court.paddle_width
            && (self.ball_y - self.right_y).abs() <= half_paddle + radius
        {
            self.ball_x = court.right_x - radius;
            self.bounce_from_paddle(-1.0, self.right_y, half_paddle, settings);
            sound_events.push(SoundEvent::PaddleHit);
        }

        if self.ball_x + radius < 0.0 {
            self.right_score += 1;
            sound_events.push(SoundEvent::ScorePoint);
            self.reset_ball(settings, Some(-1.0));
        } else if self.ball_x - radius > self.width {
            self.left_score += 1;
            sound_events.push(SoundEvent::ScorePoint);
            self.reset_ball(settings, Some(1.0));
        }

        if self.left_score.max(self.right_score) >= 11
            && self.left_score.abs_diff(self.right_score) >= 2
        {
            self.game_over = true;
            self.winner = if settings.players == 2 {
                if self.left_score > self.right_score {
                    "PLAYER 1"
                } else {
                    "PLAYER 2"
                }
            } else if self.left_score > self.right_score {
                "YOU"
            } else {
                "COMPUTER"
            }
            .to_owned();
        }
        sound_events
    }

    fn reset_ball(&mut self, settings: &Settings, direction: Option<f32>) {
        let direction =
            direction.unwrap_or_else(|| if rand::thread_rng().gen() { 1.0 } else { -1.0 });
        self.ball_x = self.width / 2.0;
        self.ball_y = self.height / 2.0;
        self.serve_direction = direction;
        if settings.autoserve {
            self.launch_ball(settings);
        } else {
            self.ball_vx = 0.0;
            self.ball_vy = 0.0;
            self.waiting_to_serve = true;
            self.serve_remaining = 0.0;
        }
    }

    fn launch_ball(&mut self, settings: &Settings) {
        let angle = settings.angle_degrees.to_radians();
        self.ball_vx = self.serve_direction * self.ball_speed * angle.cos();
        self.ball_vy =
            if rand::thread_rng().gen() { 1.0 } else { -1.0 } * self.ball_speed * angle.sin();
        self.waiting_to_serve = false;
        self.serve_remaining = 0.65;
    }

    fn bounce_from_paddle(
        &mut self,
        direction: f32,
        paddle_y: f32,
        half_paddle: f32,
        settings: &Settings,
    ) {
        let offset = ((self.ball_y - paddle_y) / half_paddle).clamp(-1.0, 1.0);
        let angle = (settings.angle_degrees + offset.abs() * 24.0).to_radians();
        let speed = self.ball_vx.hypot(self.ball_vy);
        self.ball_vx = direction * speed * angle.cos();
        self.ball_vy = if offset >= 0.0 { 1.0 } else { -1.0 } * speed * angle.sin();
    }
}

fn move_paddle(
    position: f32,
    direction: f32,
    speed: f32,
    elapsed: f32,
    court: Court,
    half_height: f32,
) -> f32 {
    (position + direction * speed * elapsed)
        .max(court.top + half_height)
        .min(court.bottom - half_height)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn active_settings() -> Settings {
        Settings {
            autoserve: true,
            ..Settings::default()
        }
    }

    #[test]
    fn autoserve_is_off_by_default() {
        let settings = Settings::default();
        assert!(!settings.autoserve);
        assert!(Game::new(&settings, 800.0, 600.0).waiting_to_serve());
    }

    #[test]
    fn paddle_and_ball_sizes_scale_with_window_resize() {
        let settings = Settings::default();
        let original = Court::new(800.0, 600.0, &settings);
        let wider = Court::new(1600.0, 600.0, &settings);
        let scale = 2.0_f32.sqrt();

        assert!((wider.paddle_width - original.paddle_width * scale).abs() < 0.0001);
        assert!((wider.paddle_height - original.paddle_height * scale).abs() < 0.0001);
        assert!((wider.ball_radius - original.ball_radius * scale).abs() < 0.0001);
    }

    #[test]
    fn manual_serve_waits_and_launches_in_the_stored_direction() {
        let settings = Settings {
            autoserve: false,
            ..Settings::default()
        };
        let mut game = Game::new(&settings, 800.0, 600.0);
        assert!(game.waiting_to_serve());
        assert_eq!((game.ball_vx, game.ball_vy), (0.0, 0.0));
        game.serve(&settings);
        assert!(!game.waiting_to_serve());
        assert!(game.ball_vx.abs() > 0.0);
        assert!(game.serve_remaining > 0.0);
    }

    #[test]
    fn pause_freezes_gameplay_until_resumed() {
        let settings = active_settings();
        let mut game = Game::new(&settings, 800.0, 600.0);
        game.serve_remaining = 0.0;
        let original_ball = (game.ball_x, game.ball_y);
        let original_paddle = game.left_y;

        game.toggle_pause();
        assert!(game.is_paused());
        assert!(game.tick(&settings, 0.05, 1.0, 0.0).is_empty());
        assert_eq!((game.ball_x, game.ball_y), original_ball);
        assert_eq!(game.left_y, original_paddle);

        game.toggle_pause();
        game.tick(&settings, 0.05, 1.0, 0.0);
        assert!(!game.is_paused());
        assert_ne!((game.ball_x, game.ball_y), original_ball);
        assert_ne!(game.left_y, original_paddle);
    }

    #[test]
    fn winning_requires_eleven_and_a_two_point_lead() {
        let settings = active_settings();
        let mut game = Game::new(&settings, 800.0, 600.0);
        game.left_score = 10;
        game.right_score = 10;
        game.serve_remaining = 0.0;
        game.ball_x = game.width + Court::new(game.width, game.height, &settings).ball_radius + 1.0;
        game.ball_vx = 0.0;
        game.ball_vy = 0.0;
        let events = game.tick(&settings, 0.01, 0.0, 0.0);
        assert!(!game.game_over);
        assert_eq!(events, vec![SoundEvent::ScorePoint]);

        game.serve_remaining = 0.0;
        game.ball_x = game.width + Court::new(game.width, game.height, &settings).ball_radius + 1.0;
        game.ball_vx = 0.0;
        game.ball_vy = 0.0;
        let events = game.tick(&settings, 0.01, 0.0, 0.0);
        assert!(game.game_over);
        assert_eq!((game.left_score, game.right_score), (12, 10));
        assert_eq!(game.winner, "YOU");
        assert_eq!(events, vec![SoundEvent::ScorePoint]);
    }

    #[test]
    fn wall_bounce_emits_a_sound_event() {
        let settings = active_settings();
        let mut game = Game::new(&settings, 800.0, 600.0);
        let court = Court::new(game.width, game.height, &settings);
        for (ball_y, ball_vy) in [
            (court.top + court.ball_radius + 1.0, -100.0),
            (court.bottom - court.ball_radius - 1.0, 100.0),
        ] {
            game.serve_remaining = 0.0;
            game.ball_x = game.width / 2.0;
            game.ball_y = ball_y;
            game.ball_vx = 0.0;
            game.ball_vy = ball_vy;

            assert_eq!(
                game.tick(&settings, 0.05, 0.0, 0.0),
                vec![SoundEvent::WallBounce]
            );
        }
    }

    #[test]
    fn paddle_hit_emits_a_sound_event() {
        let settings = active_settings();
        let mut game = Game::new(&settings, 800.0, 600.0);
        let court = Court::new(game.width, game.height, &settings);
        game.serve_remaining = 0.0;
        game.ball_x = court.left_x + court.paddle_width + court.ball_radius + 5.0;
        game.ball_y = game.left_y;
        game.ball_vx = -200.0;
        game.ball_vy = 0.0;

        assert_eq!(
            game.tick(&settings, 0.05, 0.0, 0.0),
            vec![SoundEvent::PaddleHit]
        );
    }

    #[test]
    fn resize_keeps_objects_in_the_same_relative_position() {
        let mut game = Game::new(&Settings::default(), 800.0, 600.0);
        game.ball_x = 200.0;
        game.ball_y = 150.0;
        game.resize(1600.0, 1200.0);
        assert_eq!((game.ball_x, game.ball_y), (400.0, 300.0));
    }
}
