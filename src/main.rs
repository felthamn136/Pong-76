mod audio;
mod game;

use audio::Audio;
use eframe::egui::{self, Align2, Color32, Context, FontId, Id, Pos2, Rect, Sense, Stroke, Vec2};
use game::{Controls, Court, Game, GameColour, PaddleSize, Settings, SoundEvent};
use std::time::Duration;

const DESCRIPTION: &str = "This experimental Copilot AI-developed game is inspired by the classic Squash game found on late-1970s Grandstand TV gaming consoles, including the Adman Grandstand 3000 and Video Sports Centre 6000 Colour. The project was created through a series of carefully engineered prompts designed by Neil Feltham to explore the capabilities of modern AI-assisted game development.";
const BLACK: Color32 = Color32::BLACK;
const CREAM: Color32 = Color32::from_rgb(244, 232, 193);
const MUTED: Color32 = Color32::from_rgb(208, 208, 208);

#[derive(Clone, Copy, PartialEq, Eq)]
enum Screen {
    Attraction,
    Setup,
    Game,
}

#[derive(Clone, Copy)]
enum Action {
    None,
    Continue,
    Start,
    Setup,
    Serve,
}

#[derive(Clone, Copy, Hash)]
enum SettingId {
    Players,
    Paddle,
    Angle,
    Speed,
    Scanlines,
    Controls,
    Colour,
    Autoserve,
}

struct PongApp {
    screen: Screen,
    settings: Settings,
    logo: egui::TextureHandle,
    game: Option<Game>,
    notice: Option<String>,
    audio: Option<Audio>,
    audio_error: Option<String>,
    gilrs: Option<gilrs::Gilrs>,
    joystick_ids: Vec<gilrs::GamepadId>,
    joystick_south_pressed: Vec<bool>,
}

impl PongApp {
    fn new(ctx: &Context) -> Result<Self, Box<dyn std::error::Error + Send + Sync>> {
        let image = image::load_from_memory(include_bytes!("../assets/pong76-logo.png"))?;
        let rgba = image.to_rgba8();
        let size = [rgba.width() as usize, rgba.height() as usize];
        let logo_image = egui::ColorImage::from_rgba_unmultiplied(size, rgba.as_raw());
        let logo = ctx.load_texture("pong76-logo", logo_image, egui::TextureOptions::LINEAR);
        let (audio, audio_error) = match Audio::new() {
            Ok(audio) => (Some(audio), None),
            Err(error) => {
                eprintln!("Audio initialization failed: {error}");
                (None, Some(error))
            }
        };
        Ok(Self {
            screen: Screen::Attraction,
            settings: Settings::default(),
            logo,
            game: None,
            notice: None,
            audio,
            audio_error,
            gilrs: None,
            joystick_ids: Vec::new(),
            joystick_south_pressed: Vec::new(),
        })
    }
}

impl PongApp {
    fn draw_logo_image(&self, painter: &egui::Painter, rect: Rect, width_scale: f32, y_scale: f32) {
        let logo_size = self.logo.size_vec2();
        let logo_width = rect.width() * width_scale;
        let logo_height = logo_width * logo_size.y / logo_size.x;
        let logo_rect = Rect::from_center_size(
            Pos2::new(rect.center().x, rect.top() + rect.height() * y_scale),
            Vec2::new(logo_width, logo_height),
        );
        painter.image(
            self.logo.id(),
            logo_rect,
            Rect::from_min_max(Pos2::ZERO, Pos2::new(1.0, 1.0)),
            Color32::WHITE,
        );
    }

    fn begin_match(&mut self, size: Vec2) {
        if self.settings.controls == Controls::Joystick {
            match gilrs::Gilrs::new() {
                Ok(mut manager) => {
                    while manager.next_event().is_some() {}
                    let ids: Vec<_> = manager.gamepads().map(|(id, _)| id).collect();
                    if ids.len() < self.settings.players {
                        self.notice = Some(format!(
                            "Connect {} joystick{} before starting.",
                            self.settings.players,
                            if self.settings.players == 1 { "" } else { "s" }
                        ));
                        return;
                    }
                    self.joystick_ids = ids.into_iter().take(self.settings.players).collect();
                    self.joystick_south_pressed = vec![false; self.joystick_ids.len()];
                    self.gilrs = Some(manager);
                }
                Err(error) => {
                    self.notice = Some(format!("Joystick support unavailable: {error}"));
                    return;
                }
            }
        }

        self.notice = None;
        self.game = Some(Game::new(&self.settings, size.x.max(1.0), size.y.max(1.0)));
        self.screen = Screen::Game;
    }

    fn finish_match(&mut self) {
        self.game = None;
        self.screen = Screen::Setup;
        self.joystick_ids.clear();
        self.joystick_south_pressed.clear();
        self.gilrs = None;
    }

    fn tick_game(&mut self, ctx: &Context, size: Vec2) {
        let (escape, keyboard_serve, keyboard_replay, keyboard_left, keyboard_right) =
            ctx.input(|input| {
                let escape = input.key_pressed(egui::Key::Escape);
                let serve = input.key_pressed(egui::Key::Space);
                let replay = input.key_pressed(egui::Key::Enter);
                let keyboard_controls = self.settings.controls == Controls::Keyboard;
                let left = if keyboard_controls {
                    f32::from(input.key_down(egui::Key::S))
                        - f32::from(input.key_down(egui::Key::W))
                } else {
                    0.0
                };
                let right = if keyboard_controls && self.settings.players == 2 {
                    f32::from(input.key_down(egui::Key::ArrowDown))
                        - f32::from(input.key_down(egui::Key::ArrowUp))
                } else {
                    0.0
                };
                (escape, serve, replay, left, right)
            });

        let (joystick_left, joystick_right, joystick_action) = if self.settings.controls
            == Controls::Joystick
        {
            if let Some(manager) = self.gilrs.as_mut() {
                while manager.next_event().is_some() {}
                manager.inc();
                let states: Vec<_> = self
                    .joystick_ids
                    .iter()
                    .map(|id| {
                        let gamepad = manager.gamepad(*id);
                        let stick_y = gamepad.value(gilrs::Axis::LeftStickY);
                        let dpad_y = f32::from(gamepad.is_pressed(gilrs::Button::DPadDown))
                            - f32::from(gamepad.is_pressed(gilrs::Button::DPadUp));
                        let movement = if stick_y.abs() > 0.18 {
                            stick_y
                        } else {
                            dpad_y
                        };
                        (movement, gamepad.is_pressed(gilrs::Button::South))
                    })
                    .collect();
                let action = states
                    .iter()
                    .zip(&self.joystick_south_pressed)
                    .any(|((_, pressed), was_pressed)| *pressed && !was_pressed);
                self.joystick_south_pressed = states.iter().map(|(_, pressed)| *pressed).collect();
                (
                    states.first().map_or(0.0, |(movement, _)| *movement),
                    if self.settings.players == 2 {
                        states.get(1).map_or(0.0, |(movement, _)| *movement)
                    } else {
                        0.0
                    },
                    action,
                )
            } else {
                self.joystick_south_pressed.fill(false);
                (0.0, 0.0, false)
            }
        } else {
            self.joystick_south_pressed.fill(false);
            (0.0, 0.0, false)
        };

        let (left, right) = if self.settings.controls == Controls::Joystick {
            (joystick_left, joystick_right)
        } else {
            (keyboard_left, keyboard_right)
        };

        let serve = keyboard_serve || joystick_action;
        let replay = keyboard_replay || joystick_action;
        let Some(game) = self.game.as_mut() else {
            return;
        };
        game.resize(size.x, size.y);

        if escape {
            self.finish_match();
            return;
        }
        if game.game_over {
            if replay {
                game.reset_match(&self.settings);
            }
            return;
        }
        if serve {
            game.serve(&self.settings);
        }

        let dt = ctx.input(|input| input.stable_dt);
        let sound_events = game.tick(&self.settings, dt, left, right);
        for event in sound_events {
            self.play_sound(event);
        }
    }

    fn play_sound(&mut self, event: SoundEvent) {
        let result = match self.audio.as_ref() {
            Some(audio) => audio.play(event),
            None => return,
        };
        if let Err(error) = result {
            eprintln!("Audio playback failed: {error}");
            self.audio_error = Some(error);
            self.audio = None;
        }
    }

    fn draw_attraction(&mut self, ui: &mut egui::Ui, rect: Rect) -> Action {
        let painter = ui.painter().clone();
        self.draw_logo_image(&painter, rect, 0.52, 0.21);

        let body_font = FontId::proportional((rect.width() * 0.02).max(12.0));
        let max_width = rect.width() * 0.78;
        let lines = wrap_text(ui.ctx(), DESCRIPTION, body_font.clone(), max_width);
        let line_height = body_font.size + (rect.height() * 0.008).max(3.0);
        let mut y = rect.height() * 0.43;
        for line in lines {
            let galley = ui
                .ctx()
                .fonts(|fonts| fonts.layout_no_wrap(line, body_font.clone(), MUTED));
            let pos = Pos2::new(rect.center().x - galley.size().x / 2.0, rect.top() + y);
            painter.galley(pos, galley, MUTED);
            y += line_height;
        }

        let button_size = Vec2::new(220.0, 48.0);
        let button_y = (y + (rect.height() * 0.03).max(16.0)).min(rect.height() - 72.0);
        let button_rect = Rect::from_center_size(
            Pos2::new(rect.center().x, rect.top() + button_y + button_size.y / 2.0),
            button_size,
        );
        if ui
            .put(
                button_rect,
                egui::Button::new(
                    egui::RichText::new("Continue to Game")
                        .size(16.0)
                        .strong()
                        .color(BLACK),
                )
                .fill(CREAM)
                .stroke(Stroke::NONE),
            )
            .clicked()
        {
            Action::Continue
        } else {
            Action::None
        }
    }

    fn draw_setup(&mut self, ui: &mut egui::Ui, rect: Rect) -> Action {
        let painter = ui.painter().clone();
        self.draw_logo_image(&painter, rect, 0.22, 0.13);
        painter.text(
            Pos2::new(rect.center().x, rect.top() + rect.height() * 0.25),
            Align2::CENTER_CENTER,
            "GAME SETUP",
            FontId::proportional(24.0),
            CREAM,
        );

        let cell_width = ((rect.width().min(640.0) - 24.0) / 4.0).clamp(84.0, 150.0);
        let gap = 6.0;
        let grid_width = cell_width * 4.0 + gap * 3.0;
        let grid_left = rect.center().x - grid_width / 2.0;
        let slider_height = 136.0_f32.min((rect.height() * 0.24).max(96.0));
        let row_gap = (rect.height() * 0.035).max(8.0);
        let first_y = rect.top() + rect.height() * 0.32;
        let second_y = first_y + slider_height + row_gap + 18.0;

        let mut action = Action::None;
        for (index, id) in [
            SettingId::Players,
            SettingId::Paddle,
            SettingId::Angle,
            SettingId::Speed,
            SettingId::Scanlines,
            SettingId::Controls,
            SettingId::Colour,
            SettingId::Autoserve,
        ]
        .into_iter()
        .enumerate()
        {
            let row = index / 4;
            let column = index % 4;
            let left = grid_left + column as f32 * (cell_width + gap);
            let top = if row == 0 { first_y } else { second_y };
            let title = setting_title(id);
            painter.text(
                Pos2::new(left + cell_width / 2.0, top - 8.0),
                Align2::CENTER_BOTTOM,
                title,
                FontId::proportional(11.0),
                MUTED,
            );
            let slider_rect =
                Rect::from_min_size(Pos2::new(left, top), Vec2::new(cell_width, slider_height));
            let selected = self.setting_value(id);
            if let Some(new_value) =
                draw_setting_slider(ui, slider_rect, id, &setting_choices(id), selected)
            {
                self.set_setting(id, new_value);
                self.notice = None;
            }
        }

        let notice = self.notice.as_deref().or_else(|| {
            self.audio_error
                .as_ref()
                .map(|_| "Sound output unavailable; see terminal for details.")
        });
        if let Some(notice) = notice {
            painter.text(
                Pos2::new(rect.center().x, rect.top() + rect.height() * 0.83),
                Align2::CENTER_CENTER,
                notice,
                FontId::proportional(14.0),
                Color32::from_rgb(255, 120, 100),
            );
        }
        let start_rect = Rect::from_center_size(
            Pos2::new(rect.center().x, rect.top() + rect.height() * 0.91),
            Vec2::new(170.0, 42.0),
        );
        if ui
            .put(
                start_rect,
                egui::Button::new(
                    egui::RichText::new("Start Game")
                        .size(14.0)
                        .strong()
                        .color(CREAM),
                )
                .fill(Color32::from_rgb(36, 36, 36))
                .stroke(Stroke::new(1.0_f32, Color32::from_rgb(80, 68, 46))),
            )
            .clicked()
        {
            action = Action::Start;
        }
        action
    }

    fn draw_game(&mut self, ui: &mut egui::Ui, rect: Rect) -> Action {
        let Some(game) = self.game.as_ref() else {
            return Action::Setup;
        };
        let painter = ui.painter().clone();
        let court = Court::new(rect.width(), rect.height(), &self.settings);
        let color = game_colour(self.settings.colour);
        let center_x = rect.center().x;
        if self.audio_error.is_some() {
            painter.text(
                Pos2::new(center_x, rect.top() + rect.height() * 0.12),
                Align2::CENTER_CENTER,
                "SOUND OUTPUT UNAVAILABLE",
                FontId::proportional(12.0),
                Color32::from_rgb(255, 120, 100),
            );
        }
        let top = rect.top() + court.top;
        let bottom = rect.top() + court.bottom;

        let mut dash_y = top;
        while dash_y < bottom {
            painter.line_segment(
                [
                    Pos2::new(center_x, dash_y),
                    Pos2::new(center_x, (dash_y + 8.0).min(bottom)),
                ],
                Stroke::new(4.0_f32, Color32::from_rgb(86, 86, 86)),
            );
            dash_y += 18.0;
        }

        let paddle_half = court.paddle_height / 2.0;
        let left = Rect::from_min_max(
            Pos2::new(
                rect.left() + court.left_x,
                rect.top() + game.left_y - paddle_half,
            ),
            Pos2::new(
                rect.left() + court.left_x + court.paddle_width,
                rect.top() + game.left_y + paddle_half,
            ),
        );
        let right = Rect::from_min_max(
            Pos2::new(
                rect.left() + court.right_x,
                rect.top() + game.right_y - paddle_half,
            ),
            Pos2::new(
                rect.left() + court.right_x + court.paddle_width,
                rect.top() + game.right_y + paddle_half,
            ),
        );
        painter.rect_filled(left, 0.0, color);
        painter.rect_filled(right, 0.0, color);

        if !game.game_over {
            let radius = court.ball_radius;
            let ball = Rect::from_center_size(
                Pos2::new(rect.left() + game.ball_x, rect.top() + game.ball_y),
                Vec2::splat(radius * 2.0),
            );
            painter.rect_filled(ball, 0.0, color);
        }

        let left_label = if self.settings.players == 2 {
            "PLAYER 1"
        } else {
            "YOU"
        };
        let right_label = if self.settings.players == 2 {
            "PLAYER 2"
        } else {
            "COMPUTER"
        };
        let score_font = FontId::proportional((rect.width() * 0.0325).max(10.0));
        painter.text(
            Pos2::new(
                rect.left() + rect.width() * 0.25,
                rect.top() + rect.height() * 0.07,
            ),
            Align2::CENTER_CENTER,
            format!("{left_label}  {}", game.left_score),
            score_font.clone(),
            color,
        );
        painter.text(
            Pos2::new(
                rect.left() + rect.width() * 0.75,
                rect.top() + rect.height() * 0.07,
            ),
            Align2::CENTER_CENTER,
            format!("{right_label}  {}", game.right_score),
            score_font,
            color,
        );

        let mut action = Action::None;
        if game.game_over {
            let replay_prompt = if self.settings.controls == Controls::Joystick {
                "PRESS SOUTH / ENTER TO PLAY AGAIN"
            } else {
                "PRESS ENTER TO PLAY AGAIN"
            };
            painter.text(
                rect.center(),
                Align2::CENTER_CENTER,
                format!("{} WINS\n{replay_prompt}", game.winner),
                FontId::proportional((rect.width() * 0.04).max(14.0)),
                color,
            );
        }

        let controls_y = rect.top() + rect.height() * 0.95;
        let mut labels = match (self.settings.controls, self.settings.players) {
            (Controls::Joystick, _) => vec!["JOYSTICK: MOVE"],
            (Controls::Keyboard, 2) => vec!["P1: W/S  |  P2: UP/DOWN"],
            _ => vec!["W/S: MOVE"],
        };
        if !self.settings.autoserve && game.waiting_to_serve() && !game.game_over {
            labels.push(if self.settings.controls == Controls::Joystick {
                "SOUTH / SPACE: SERVE"
            } else {
                "SPACE: SERVE"
            });
        }
        labels.push("ESC: SETUP");
        let total_width = labels
            .iter()
            .map(|label| label.len() as f32 * (rect.width() * 0.008).max(7.0) + 32.0)
            .sum::<f32>()
            + (labels.len().saturating_sub(1) as f32 * 6.0);
        let mut x = center_x - total_width / 2.0;
        for label in labels {
            let width = label.len() as f32 * (rect.width() * 0.008).max(7.0) + 32.0;
            let button_rect = Rect::from_center_size(
                Pos2::new(x + width / 2.0, controls_y),
                Vec2::new(width, 32.0),
            );
            if ui
                .put(
                    button_rect,
                    egui::Button::new(
                        egui::RichText::new(label)
                            .size((rect.width() * 0.014).max(8.0))
                            .strong()
                            .color(CREAM),
                    )
                    .fill(Color32::from_rgb(36, 36, 36))
                    .stroke(Stroke::new(1.0_f32, Color32::from_rgb(80, 80, 80))),
                )
                .clicked()
            {
                action = if label.starts_with("SPACE") {
                    Action::Serve
                } else if label.starts_with("ESC") {
                    Action::Setup
                } else {
                    Action::None
                };
            }
            x += width + 6.0;
        }
        action
    }

    fn setting_value(&self, id: SettingId) -> usize {
        match id {
            SettingId::Players => self.settings.players - 1,
            SettingId::Paddle => usize::from(self.settings.paddle_size == PaddleSize::Large),
            SettingId::Angle => usize::from(self.settings.angle_degrees > 20.0),
            SettingId::Speed => usize::from(self.settings.fast),
            SettingId::Scanlines => usize::from(!self.settings.scanlines),
            SettingId::Controls => usize::from(self.settings.controls == Controls::Joystick),
            SettingId::Colour => match self.settings.colour {
                GameColour::White => 0,
                GameColour::Green => 1,
                GameColour::Amber => 2,
            },
            SettingId::Autoserve => usize::from(!self.settings.autoserve),
        }
    }

    fn set_setting(&mut self, id: SettingId, value: usize) {
        match id {
            SettingId::Players => self.settings.players = value + 1,
            SettingId::Paddle => {
                self.settings.paddle_size = if value == 0 {
                    PaddleSize::Small
                } else {
                    PaddleSize::Large
                }
            }
            SettingId::Angle => self.settings.angle_degrees = if value == 0 { 20.0 } else { 40.0 },
            SettingId::Speed => self.settings.fast = value != 0,
            SettingId::Scanlines => self.settings.scanlines = value == 0,
            SettingId::Controls => {
                self.settings.controls = if value == 0 {
                    Controls::Keyboard
                } else {
                    Controls::Joystick
                }
            }
            SettingId::Colour => {
                self.settings.colour = match value {
                    1 => GameColour::Green,
                    2 => GameColour::Amber,
                    _ => GameColour::White,
                }
            }
            SettingId::Autoserve => self.settings.autoserve = value == 0,
        }
    }
}

impl eframe::App for PongApp {
    fn update(&mut self, ctx: &Context, _frame: &mut eframe::Frame) {
        let size = ctx.available_rect().size();
        if self.screen == Screen::Game {
            self.tick_game(ctx, size);
        }

        let mut action = Action::None;
        egui::CentralPanel::default()
            .frame(egui::Frame::none().fill(BLACK))
            .show(ctx, |ui| {
                let rect = ui.max_rect();
                ui.painter().rect_filled(rect, 0.0, BLACK);
                if self.settings.scanlines {
                    draw_scanlines(ui.painter(), rect, ui.ctx().pixels_per_point());
                }
                action = match self.screen {
                    Screen::Attraction => self.draw_attraction(ui, rect),
                    Screen::Setup => self.draw_setup(ui, rect),
                    Screen::Game => self.draw_game(ui, rect),
                };
            });

        match action {
            Action::Continue => {
                self.screen = Screen::Setup;
                self.notice = None;
            }
            Action::Start => self.begin_match(size),
            Action::Setup => self.finish_match(),
            Action::Serve => {
                if let Some(game) = self.game.as_mut() {
                    game.serve(&self.settings);
                }
            }
            Action::None => {}
        }

        if self.screen == Screen::Game {
            ctx.request_repaint_after(Duration::from_millis(16));
        }
    }
}

fn setting_title(id: SettingId) -> &'static str {
    match id {
        SettingId::Players => "PLAYER MODE",
        SettingId::Paddle => "PADDLE SIZE",
        SettingId::Angle => "BALL ANGLE",
        SettingId::Speed => "GAME SPEED",
        SettingId::Scanlines => "SCANLINES",
        SettingId::Controls => "CONTROLS",
        SettingId::Colour => "GAME COLOUR",
        SettingId::Autoserve => "AUTO SERVE",
    }
}

fn setting_choices(id: SettingId) -> &'static [&'static str] {
    match id {
        SettingId::Players => &["PLAYER 1", "PLAYER 2"],
        SettingId::Paddle => &["SMALL", "LARGE"],
        SettingId::Angle => &["20 DEGREES", "40 DEGREES"],
        SettingId::Speed => &["SLOW", "FAST"],
        SettingId::Scanlines => &["ON", "OFF"],
        SettingId::Controls => &["KEYBOARD", "JOYSTICK"],
        SettingId::Colour => &["WHITE", "GREEN", "AMBER"],
        SettingId::Autoserve => &["YES", "NO"],
    }
}

fn draw_setting_slider(
    ui: &mut egui::Ui,
    rect: Rect,
    id: SettingId,
    choices: &[&str],
    selected: usize,
) -> Option<usize> {
    let response = ui.interact(rect, Id::new(("setting", id)), Sense::click_and_drag());
    let painter = ui.painter();
    painter.rect_filled(rect, 0.0, Color32::from_rgb(33, 26, 18));
    painter.rect_stroke(
        rect,
        0.0,
        Stroke::new(2.0_f32, Color32::from_rgb(162, 122, 69)),
    );

    let scale = rect.height() / 136.0;
    let track_top = rect.top() + 42.0 * scale;
    let track_bottom = rect.top() + 92.0 * scale;
    let track_x = rect.center().x;
    painter.line_segment(
        [
            Pos2::new(track_x, track_top),
            Pos2::new(track_x, track_bottom),
        ],
        Stroke::new(18.0 * scale, Color32::from_rgb(112, 83, 47)),
    );
    painter.line_segment(
        [
            Pos2::new(track_x, track_top),
            Pos2::new(track_x, track_bottom),
        ],
        Stroke::new(2.0 * scale, Color32::from_rgb(196, 154, 94)),
    );

    let positions: Vec<f32> = if choices.len() == 1 {
        vec![track_top]
    } else {
        (0..choices.len())
            .map(|index| {
                track_top + index as f32 * (track_bottom - track_top) / (choices.len() - 1) as f32
            })
            .collect()
    };
    for (index, label) in choices.iter().enumerate() {
        let y = if index == 0 {
            rect.top() + 17.0 * scale
        } else if index == choices.len() - 1 {
            rect.bottom() - 17.0 * scale
        } else {
            positions[index]
        };
        let color = if index == selected {
            Color32::from_rgb(255, 225, 163)
        } else {
            Color32::from_rgb(156, 135, 96)
        };
        painter.text(
            Pos2::new(rect.center().x, y),
            Align2::CENTER_CENTER,
            *label,
            FontId::proportional((9.0 * scale).max(7.0)),
            color,
        );
    }

    let knob_y = positions[selected.min(positions.len() - 1)];
    let knob = Rect::from_center_size(
        Pos2::new(track_x, knob_y),
        Vec2::new(32.0 * scale, 20.0 * scale),
    );
    painter.rect_filled(knob, 0.0, Color32::from_rgb(198, 154, 85));
    painter.rect_stroke(
        knob,
        0.0,
        Stroke::new(2.0_f32, Color32::from_rgb(255, 224, 160)),
    );
    painter.line_segment(
        [
            Pos2::new(track_x - 5.0 * scale, knob_y - 6.0 * scale),
            Pos2::new(track_x - 5.0 * scale, knob_y + 6.0 * scale),
        ],
        Stroke::new(2.0_f32, Color32::from_rgb(255, 232, 181)),
    );
    painter.line_segment(
        [
            Pos2::new(track_x + 5.0 * scale, knob_y - 6.0 * scale),
            Pos2::new(track_x + 5.0 * scale, knob_y + 6.0 * scale),
        ],
        Stroke::new(2.0_f32, Color32::from_rgb(104, 75, 41)),
    );

    if response.dragged() || response.clicked() {
        if let Some(pos) = response.interact_pointer_pos() {
            let selected = positions
                .iter()
                .enumerate()
                .min_by(|(_, a), (_, b)| (pos.y - **a).abs().total_cmp(&(pos.y - **b).abs()))
                .map(|(index, _)| index);
            return selected;
        }
    }
    None
}

fn wrap_text(ctx: &Context, text: &str, font: FontId, max_width: f32) -> Vec<String> {
    let mut lines = Vec::new();
    let mut line = String::new();
    for word in text.split_whitespace() {
        let candidate = if line.is_empty() {
            word.to_owned()
        } else {
            format!("{line} {word}")
        };
        let width = ctx.fonts(|fonts| {
            fonts
                .layout_no_wrap(candidate.clone(), font.clone(), MUTED)
                .size()
                .x
        });
        if !line.is_empty() && width > max_width {
            lines.push(std::mem::take(&mut line));
            line.push_str(word);
        } else {
            line = candidate;
        }
    }
    if !line.is_empty() {
        lines.push(line);
    }
    lines
}

fn draw_scanlines(painter: &egui::Painter, rect: Rect, pixels_per_point: f32) {
    let pixels_per_point = pixels_per_point.max(f32::EPSILON);
    let pixel_height = 1.0 / pixels_per_point;
    let color = Color32::from_gray(32);
    let mut y = (rect.top() * pixels_per_point).ceil() / pixels_per_point;
    while y < rect.bottom() {
        let line = Rect::from_min_max(
            Pos2::new(rect.left(), y),
            Pos2::new(rect.right(), (y + pixel_height).min(rect.bottom())),
        );
        painter.rect_filled(line, 0.0, color);
        y += pixel_height * 2.0;
    }
}

fn game_colour(colour: GameColour) -> Color32 {
    let (r, g, b) = colour.rgb();
    Color32::from_rgb(r, g, b)
}

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_title("Pong '76")
            .with_inner_size([800.0, 600.0]),
        ..Default::default()
    };
    eframe::run_native(
        "Pong '76",
        options,
        Box::new(|creation_context| Ok(Box::new(PongApp::new(&creation_context.egui_ctx)?))),
    )
}
