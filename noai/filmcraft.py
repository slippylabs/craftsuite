"""FilmCraft without AI.

The web build already compiles without Whisper (speech-to-text) and Kokoro
(neural voices) -- those are cargo features it never enables -- but their UI
and commands were still there, failing with "not available in this build".
This takes them out: the Transcribe button, Transcribe Sequence, the speech
model and voice download commands, the "Natural voices" list and its
download box, and the Transcription settings. Transcripts you IMPORT, and the
built-in formant voices, are not AI and stay.
"""
from _patch import sub

# Text panel: no Transcribe button, just how to get a transcript in.
sub("crates/ui-egui/src/panels/text.rs",
    """        let note = if filmcraft_speech_available(app) {
            tl!("Speech-to-text turns the dialogue into editable text.")
        } else {
            tl!("This build has no speech-to-text; import a transcript with transcript.set.")
        };
        ui.painter().text(c - vec2(0.0, 8.0), Align2::CENTER_CENTER, note, Tokens::ui(12.0), t.text_dim);
        let r = Rect::from_center_size(c + vec2(0.0, 26.0), vec2(200.0, 26.0));
        let resp = ui.interact(r, egui::Id::new("text.transcript.generate"), Sense::click());
        ui.painter().rect_filled(r, 13.0, if resp.hovered() { t.accent_hover } else { t.accent });
        ui.painter().text(r.center(), Align2::CENTER_CENTER, tl!("Transcribe"), Tokens::semibold(12.0), Color32::WHITE);
        app.auto.add("text.transcript.generate", r, "Transcribe");
        if resp.clicked() {
            actions.push(("transcript.generate".into(), json!({})));
        }
""",
    """        let note = tl!("This sequence has no transcript.");
        ui.painter().text(c - vec2(0.0, 8.0), Align2::CENTER_CENTER, note, Tokens::ui(12.0), t.text_dim);
""")
sub("crates/ui-egui/src/panels/text.rs",
    """tl!("Transcribe sequence")""", """tl!("No transcript")""")

# Text to Speech: only the built-in voices are ever listed.
sub("crates/tts/src/lib.rs",
    """    formant::VOICES.iter().map(|v| v.info).chain(catalog::VOICES.iter().map(|v| VoiceInfo { installed, ..v.info })).collect()""",
    """    let _ = installed;
    formant::VOICES.iter().map(|v| v.info).collect()""")
sub("crates/ui-egui/src/panels/tts.rs",
    """            for (engine, heading) in [("neural", "Natural voices"), ("basic", "Basic voices (built in)")] {""",
    """            for (engine, heading) in [("basic", "Voices (built in)")] {""")

# Commands: no transcription, no model or voice downloads.
sub("crates/engine/src/transcript.rs",
    """        spec(
            "transcript.generate",
            "Transcribe…",
            &["Sequence", "Transcript"],
            r#"{"items":[id]?,"model":"whisper-base"?,"language":"en|auto"?,"diarize":bool?,"maxSpeakers":n?}"#,
            can_transcribe,
            generate,
            true,
        ),
""", "")
sub("crates/engine/src/transcript.rs",
    """        spec("transcript.models", "List Speech Models", &[], "{}", always, models, false),
        spec("transcript.downloadModel", "Download Speech Model", &[], r#"{"model":"whisper-base"?}"#, can_download, download_model, true),
""", "")
sub("crates/engine/src/sequence_extras.rs",
    """        spec(
            "sequence.transcribe",
            "Transcribe Sequence…",
            &["Sequence"],
            None,
            r#"{"track":"mix"|"A1"|id?,"language":"en|auto"?,"diarize":bool?,"maxSpeakers":n?,"model":str?}"#,
            can_transcribe_sequence,
            transcribe,
        ),
""", "")
sub("crates/engine/src/narration.rs",
    """        spec("tts.downloadVoices", "Download Natural Voices", r#"{"wait":bool?}"#, always, download_voices, false),
""", "")
# Auto-transcribe on import can never fire.
sub("crates/engine/src/commands.rs",
    """            if ma.auto_transcribe && ma.auto_transcribe_scope == "allImported" && !ids.is_empty() {""",
    """            if false && ma.auto_transcribe && ma.auto_transcribe_scope == "allImported" && !ids.is_empty() {""")

# Settings: Media Analysis keeps its caching options, loses Transcription.
sub("crates/engine/src/settings.rs",
    """        title: "Media Analysis & Transcription",""", """        title: "Media Analysis",""")
sub("crates/engine/src/settings.rs",
    """                "Media analysis and transcriptions will be cached""", """                "Media analysis will be cached""")
sub("crates/engine/src/settings.rs",
    """            Row::Group(
                "Transcription",
                &[
                    b("mediaAnalysis.autoTranscribe", "Automatically transcribe clips", true),
                    sub("mediaAnalysis.autoTranscribeScope", "Transcription preferences", Kind::Choice(TRANSCRIBE_SCOPE), "mediaAnalysis.autoTranscribe", true),
                    f("mediaAnalysis.speakerLabeling", "Speaker Labeling", Kind::Choice(SPEAKERS), true),
                    b("mediaAnalysis.languageAutoDetect", "Enable language auto-detection", true),
                    f("mediaAnalysis.defaultLanguage", "Default language", Kind::Choice(LANGUAGES), true),
                    f("mediaAnalysis.whisperModel", "Speech model", Kind::Choice(MODELS), true),
                ],
            ),
""", "")
sub("crates/ui-egui/src/menus.rs",
    """"Media Analysis & Transcription…\"""", """"Media Analysis…\"""")
