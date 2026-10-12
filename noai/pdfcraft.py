"""PdfCraft without AI.

Two AI features: OCR ("Scan & OCR") runs neural text detection and
recognition models (ocrs on the rten runtime), and an "AI assistant" group
(Summarize / Ask / Translate with a bring-your-own model). The browser build
ships no OCR models and the assistant has no code behind it yet, but the
runtime was compiled in and both groups were on the tools page. This drops
ocrs and rten from the build, makes the recogniser report that it is not
available, and removes both tool groups and the two OCR commands.
"""
from _patch import sub

sub("crates/ocr/Cargo.toml",
    """ocrs = { version = "0.13.1", default-features = false, features = ["rten"] }
rten = { version = "0.26.0", default-features = false, features = ["rten_format"] }
""", "")

OCR = "crates/ocr/src/lib.rs"
sub(OCR, """pub struct Ocr {
    engine: ocrs::OcrEngine,
}""", """pub struct Ocr {
    _none: (),
}""")
sub(OCR, """        let load = |p: &Path| rten::Model::load_file(p).map_err(|e| OcrError::Load(p.display().to_string(), e.to_string()));
        let params = ocrs::OcrEngineParams {
            detection_model: Some(load(&models.detection)?),
            recognition_model: Some(load(&models.recognition)?),
            alphabet: Some(ALPHABET.into()),
            ..Default::default()
        };
        let engine = ocrs::OcrEngine::new(params).map_err(|e| OcrError::Load("ocr engine".into(), e.to_string()))?;
        Ok(Ocr { engine })""", """        let _ = models;
        Err(OcrError::NoModels)""")
a = """        // ocrs wants 1 or 3 channels."""
b = """            .filter(|l| !l.words.is_empty())
            .collect())"""
import _patch
p = _patch.ROOT / OCR
s = p.read_text()
if s.count(a) != 1 or s.count(b) != 1:
    raise SystemExit("noai: crates/ocr/src/lib.rs: recognize() body moved")
i, j = s.index(a), s.index(b) + len(b)
p.write_text(s[:i] + """        let _ = &self._none;
        Err(OcrError::NoModels)""" + s[j:])

CAT = "crates/engine/src/catalog.rs"
sub(CAT, """    ToolGroup {
        id: "scan",
        label: "Scan & OCR",
        icon: "scan-text",
        hue: GREEN,
        badge: None,
        availability: Ready,
        sections: &[ToolSection {
            title: "Recognize text",
            items: &[
                item("In this file", "scan-text", "ocr.recognize", Ready),
                item("In multiple files", "files", "ocr.recognize_batch", Ready),
                item("Enhance scanned file", "sparkles", "ocr.enhance", Planned("M10")),
                item("Correct recognized text", "text-select", "ocr.correct", Planned("M10")),
            ],
        }],
    },
""", "")
sub(CAT, """    ToolGroup {
        id: "ai",
        label: "AI assistant",
        icon: "sparkles",
        hue: PINK,
        badge: Some("Optional"),
        availability: Provider,
        sections: &[ToolSection {
            title: "Bring your own model (off by default)",
            items: &[
                item("Summarize", "sparkles", "ai.summary", Provider),
                item("Ask about this document", "message-circle-reply", "ai.ask", Provider),
                item("Translate", "languages", "ai.translate", Provider),
            ],
        }],
    },
""", "")
sub("crates/engine/src/commands.rs", """    c("ocr.recognize", "Recognize text…", None, None, Modification, "scan-text"),
    c("ocr.recognize_batch", "Recognize text in multiple files…", None, None, Nothing, "files"),
""", "")

# The home page's privacy line promised cloud processing "unless you add a
# provider" -- the AI assistant's provider, which no longer exists.
sub("crates/ui-egui/src/home.rs",
    """tl!("PdfCraft works offline. No telemetry, no account, and no cloud processing unless you add a provider.")""",
    """tl!("PdfCraft works offline. No telemetry, no account, and no cloud processing.")""")
