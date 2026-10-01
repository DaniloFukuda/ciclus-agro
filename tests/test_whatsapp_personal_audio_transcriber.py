import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import api_whatsapp


AUTHORIZED_PHONE = "61998266551"
ALLOWLIST_ENV = "WHATSAPP_AUDIO_TRANSCRIBER_ALLOWLIST"


def _audio_message(sender: str, media_id: str = "media-audio") -> dict:
    return {
        "from": sender,
        "id": f"wamid.{media_id}",
        "type": "audio",
        "audio": {"id": media_id, "mime_type": "audio/ogg"},
    }


def _install_fresh_sender(monkeypatch):
    monkeypatch.setattr(
        api_whatsapp.rdv_service,
        "get_collaborator_by_phone",
        lambda phone: {"id": 1, "telefone_whatsapp": phone},
    )
    monkeypatch.setattr(api_whatsapp, "_get_active_visita_for_phone", lambda phone: None)
    monkeypatch.setattr(api_whatsapp, "_get_rdv_comment_state", lambda phone: None)
    api_whatsapp.whatsapp_menu_states.clear()
    api_whatsapp.standalone_transcription_modes.clear()


def test_allowlist_usa_normalizacao_canonica_do_projeto(monkeypatch):
    monkeypatch.setenv(ALLOWLIST_ENV, "+61 (99826-6551)")

    assert api_whatsapp._is_personal_audio_transcriber_allowed(AUTHORIZED_PHONE)
    assert not api_whatsapp._is_personal_audio_transcriber_allowed("61998266552")


def test_audio_autorizado_inicia_transcricao_avulsa_sem_comando_e_limpa_sessao(monkeypatch):
    _install_fresh_sender(monkeypatch)
    monkeypatch.setenv(ALLOWLIST_ENV, AUTHORIZED_PHONE)
    sent = []
    calls = []
    monkeypatch.setattr(api_whatsapp, "_safe_send_text", lambda to, text: sent.append((to, text)))

    def fake_transcribe(sender_phone, media_id, mime_type, **kwargs):
        calls.append(
            {
                "sender": sender_phone,
                "media_id": media_id,
                "mime_type": mime_type,
                "state": api_whatsapp.whatsapp_menu_states.get(sender_phone),
                "mode": api_whatsapp.standalone_transcription_modes.get(sender_phone),
            }
        )
        return "📝 Transcrição revisada:\n\ntexto transcrito"

    monkeypatch.setattr(api_whatsapp, "handle_whatsapp_audio_message", fake_transcribe)

    api_whatsapp._handle_whatsapp_message(_audio_message(AUTHORIZED_PHONE))

    assert calls == [
        {
            "sender": AUTHORIZED_PHONE,
            "media_id": "media-audio",
            "mime_type": "audio/ogg",
            "state": api_whatsapp.STANDALONE_TRANSCRIPTION_STATE,
            "mode": "revisada",
        }
    ]
    assert sent == [(AUTHORIZED_PHONE, "📝 Transcrição revisada:\n\ntexto transcrito")]
    assert AUTHORIZED_PHONE not in api_whatsapp.whatsapp_menu_states
    assert AUTHORIZED_PHONE not in api_whatsapp.standalone_transcription_modes


def test_segundo_audio_autorizado_e_independente_do_primeiro(monkeypatch):
    _install_fresh_sender(monkeypatch)
    monkeypatch.setenv(ALLOWLIST_ENV, AUTHORIZED_PHONE)
    calls = []
    monkeypatch.setattr(api_whatsapp, "_safe_send_text", lambda *args: None)

    def fake_transcribe(sender_phone, media_id, mime_type, **kwargs):
        calls.append((media_id, api_whatsapp.whatsapp_menu_states.get(sender_phone)))
        return "texto transcrito"

    monkeypatch.setattr(api_whatsapp, "handle_whatsapp_audio_message", fake_transcribe)

    api_whatsapp._handle_whatsapp_message(_audio_message(AUTHORIZED_PHONE, "audio-1"))
    api_whatsapp._handle_whatsapp_message(_audio_message(AUTHORIZED_PHONE, "audio-2"))

    assert calls == [
        ("audio-1", api_whatsapp.STANDALONE_TRANSCRIPTION_STATE),
        ("audio-2", api_whatsapp.STANDALONE_TRANSCRIPTION_STATE),
    ]
    assert AUTHORIZED_PHONE not in api_whatsapp.whatsapp_menu_states
    assert AUTHORIZED_PHONE not in api_whatsapp.standalone_transcription_modes


def test_audio_de_numero_fora_da_allowlist_nao_recebe_sessao_automatica(monkeypatch):
    _install_fresh_sender(monkeypatch)
    monkeypatch.setenv(ALLOWLIST_ENV, AUTHORIZED_PHONE)
    other_phone = "61998266552"
    observed_states = []
    monkeypatch.setattr(api_whatsapp, "_safe_send_text", lambda *args: None)

    def fake_transcribe(sender_phone, media_id, mime_type, **kwargs):
        observed_states.append(api_whatsapp.whatsapp_menu_states.get(sender_phone))
        return "resposta existente"

    monkeypatch.setattr(api_whatsapp, "handle_whatsapp_audio_message", fake_transcribe)

    api_whatsapp._handle_whatsapp_message(_audio_message(other_phone))

    assert observed_states == [None]
    assert other_phone not in api_whatsapp.whatsapp_menu_states
    assert other_phone not in api_whatsapp.standalone_transcription_modes


def test_mensagens_nao_audio_do_autorizado_nao_iniciam_transcricao(monkeypatch):
    _install_fresh_sender(monkeypatch)
    monkeypatch.setenv(ALLOWLIST_ENV, AUTHORIZED_PHONE)
    calls = []
    monkeypatch.setattr(api_whatsapp, "handle_whatsapp_audio_message", lambda *args, **kwargs: calls.append(args))
    monkeypatch.setattr(api_whatsapp, "_safe_send_text", lambda *args: None)

    api_whatsapp._handle_whatsapp_message(
        {"from": AUTHORIZED_PHONE, "id": "wamid.text", "type": "text", "text": {"body": "olá"}}
    )
    api_whatsapp._handle_whatsapp_message(
        {"from": AUTHORIZED_PHONE, "id": "wamid.image", "type": "image", "image": {}}
    )
    api_whatsapp._handle_whatsapp_message(
        {"from": AUTHORIZED_PHONE, "id": "wamid.document", "type": "document", "document": {}}
    )
    api_whatsapp._handle_whatsapp_message(
        {"from": AUTHORIZED_PHONE, "id": "wamid.video", "type": "video", "video": {}}
    )
    api_whatsapp._handle_whatsapp_message(
        {"from": AUTHORIZED_PHONE, "id": "wamid.location", "type": "location", "location": {}}
    )

    assert calls == []
    assert AUTHORIZED_PHONE not in api_whatsapp.whatsapp_menu_states
    assert AUTHORIZED_PHONE not in api_whatsapp.standalone_transcription_modes


def test_menu_principal_permanece_neutro_e_comando_existente_permanece(monkeypatch):
    monkeypatch.setenv(ALLOWLIST_ENV, AUTHORIZED_PHONE)

    assert api_whatsapp.MAIN_MENU_MESSAGE == "Ciclus Agro 🌱\nAtendimento em atualização."
    assert "transcrever audio" in api_whatsapp.STANDALONE_TRANSCRIPTION_COMMANDS
