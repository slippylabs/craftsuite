"""LightCraft without AI.

The browser build already compiles without AI Denoise and SAM masks (cargo
features it never enables), but their controls were still shown, and face
detection/recognition (a YuNet/SFace ONNX interpreter) is linked in with no
switch at all. This removes them: the Object and Describe mask tiles, the
AI Denoise controls and Settings tab, the Faces Settings tab, the People
view, face boxes and the face-model dialog, and every denoise.* / faces.*
command. Subject, Sky and Background masks are classical heuristics (centre-
weighted saliency, a sky colour model) and stay.
"""
from _patch import sub

sub("crates/ui-egui/src/panels/masking.rs", """        let tiles: [(&str, &str, Icon); 10] = [
            ("object", "Object", Icon::Subject),
            ("prompt", "Describe", Icon::Subject),
""", """        let tiles: [(&str, &str, Icon); 8] = [
""")

sub("crates/ui-egui/src/panels/edit.rs", """        // AI Denoise is its own tool, apart from the manual noise reduction sliders below it
        sub_title(ui, crate::i18n::tr("AI Denoise"));
        // AI Denoise: how much of the photo's cleaned picture to mix in (raw files only), and what that picture is doing
        let applicable = !matches!(app.session.denoise_photo_state(id), lightcraft_engine::denoise::PhotoState::NotApplicable);
        let on = d.enhance.denoise_enabled();
        super::denoise::detail_toggle(app, ui, id, on, applicable);
        control(app, ui, d, "enhance.denoise", applicable && on);
        super::denoise::detail_status(app, ui, id, if on { d.enhance.denoise } else { 0.0 });
""", "")

sub("crates/ui-egui/src/panels/settings.rs", """    ("faces", "Faces"),
    ("denoise", "AI Denoise"),
""", "")

sub("crates/ui-egui/src/menus.rs", """    ("view.people", "People", None, "View"),
    ("view.person", "Show Person", None, ""),
    ("view.faceBoxes", "Face Boxes", None, "View"),
""", "")
sub("crates/ui-egui/src/menus.rs", """    ("dialog.faceModel", "Add Face Model…", None, ""),
""", "")
sub("crates/ui-egui/src/menubar.rs", """            "view.people",
""", "")
sub("crates/ui-egui/src/menubar.rs", """            "view.faceBoxes",
""", "")
sub("crates/ui-egui/src/panels/bottombar.rs", """                        ("people", Icon::Subject, ViewMode::People, "People"),
""", "")

sub("crates/engine/src/cmd/mod.rs", """        v.extend(denoise::specs());
        v.extend(face_models::specs());
        v.extend(face_detect::specs());
        v.extend(face_recognize::specs());
""", "")
