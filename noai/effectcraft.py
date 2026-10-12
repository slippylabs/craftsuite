"""EffectCraft without AI.

Roto Brush and face tracking can use trained models (MobileSAM, MediaPipe
Face Landmarker). The browser build already refuses to load them, but the
neural-network code was compiled in and Settings still listed the models.
This compiles the networks out (pt/tflite readers, nn kernels, MobileSAM,
MediaPipe), empties the model registry, and removes the two Settings pages.
Roto Brush and face tracking keep their classical engines (graph cut, the
shape-model tracker), which are not AI.
"""
from _patch import sub

LIB = "crates/segment/src/lib.rs"
sub(LIB, """pub mod face;
pub mod mediapipe;
pub mod mobilesam;
pub mod nn;
pub mod pt;
pub mod tflite;
""", """pub mod face;
""")
sub(LIB, """pub const MODELS: &[ModelInfo] = &[MOBILE_SAM, FACE_LANDMARKER];""",
    """pub const MODELS: &[ModelInfo] = &[];""")
sub(LIB, """    match id {
        "mobilesam" => {
            let w = pt::read(bytes)?;
            Ok(Loaded::Mask(Arc::new(Sam { net: mobilesam::MobileSam::from_weights(&w)? })))
        }
        "mediapipe-face" => Ok(Loaded::Face(Arc::new(mediapipe::FaceLandmarker::from_task(bytes)?))),
        _ => Err(format!("no loader for `{id}`")),
    }""", """    let _ = bytes;
    Err(format!("no loader for `{id}`"))""")
sub(LIB, """struct Sam {
    net: mobilesam::MobileSam,
}

impl MaskModel for Sam {
    fn info(&self) -> &'static ModelInfo {
        &MOBILE_SAM
    }
    fn segment(&self, rgb: &[[f32; 3]], w: usize, h: usize, prompt: &Prompt) -> Result<Vec<f32>> {
        let e = self.net.embed(rgb, w, h)?;
        Ok(self.net.predict(&e, prompt).0)
    }
}
""", "")

sub("crates/engine/src/prefs.rs", """        Page {
            id: "roto",
            title: "Roto Brush",
            items: vec![
                Section("Segmentation Model"),
                Note(
                    "Roto Brush 2.0 and 3.0 use the model chosen here (Version 1.0 always uses the classic engine). Models are open source, downloaded only when you ask, and checked against their published SHA-256.",
                ),
                Models(effectcraft_segment::Task::Mask),
            ],
        },
        Page {
            id: "face",
            title: "Face Tracking",
            items: vec![
                Section("Face Model"),
                Note(
                    "Face tracking in the Tracker panel (Outline Only and Detailed Features) uses the model chosen here. Models are open source, downloaded only when you ask, and checked against their published SHA-256.",
                ),
                Models(effectcraft_segment::Task::Face),
            ],
        },
""", "")

# The roto.model.* / face.model.* commands (list, download, install, select,
# remove) only ever served those pages; nothing else runs them.
sub("crates/engine/src/commands/mod.rs", """        v.extend(crate::models::specs());
""", "")
