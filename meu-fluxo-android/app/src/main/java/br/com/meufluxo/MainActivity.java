package br.com.meufluxo;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.util.ArrayList;
import java.util.Locale;

/** Reconstructed Android host for the HTML application recovered from the APK. */
public class MainActivity extends Activity {
    private static final int MICROPHONE_PERMISSION_REQUEST = 41;
    private WebView webView;
    private SpeechRecognizer speechRecognizer;
    private boolean pendingRecognition;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        webView = new WebView(this);
        setContentView(webView);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new VoiceBridge(), "AndroidVoice");
        webView.loadUrl("file:///android_asset/gestao-gastos.html");
    }

    @Override public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack(); else super.onBackPressed();
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode == MICROPHONE_PERMISSION_REQUEST) {
            if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED && pendingRecognition) {
                pendingRecognition = false;
                startListening();
            } else {
                pendingRecognition = false;
                sendVoiceError("É preciso permitir o microfone para registrar gastos por voz.");
            }
        }
    }

    private void startListening() {
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            sendVoiceError("O reconhecimento de voz não está disponível neste aparelho."); return;
        }
        if (speechRecognizer != null) speechRecognizer.destroy();
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this);
        speechRecognizer.setRecognitionListener(new RecognitionListener() {
            public void onReadyForSpeech(Bundle params) { sendVoiceStatus("Pode falar agora."); }
            public void onBeginningOfSpeech() { sendVoiceStatus("Estou ouvindo…"); }
            public void onRmsChanged(float rmsdB) {}
            public void onBufferReceived(byte[] buffer) {}
            public void onEndOfSpeech() { sendVoiceStatus("Processando fala…"); }
            public void onError(int error) { sendVoiceError("Não consegui entender. Tente falar novamente."); }
            public void onResults(Bundle results) {
                ArrayList<String> matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                if (matches != null && !matches.isEmpty()) sendVoiceResult(matches.get(0));
                else sendVoiceError("Não consegui entender. Tente falar novamente.");
            }
            public void onPartialResults(Bundle partialResults) {}
            public void onEvent(int eventType, Bundle params) {}
        });
        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "pt-BR");
        intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Diga a descrição e o valor do gasto");
        speechRecognizer.startListening(intent);
    }

    private void callJs(String function, String value) {
        if (webView == null) return;
        final String safe = org.json.JSONObject.quote(value == null ? "" : value);
        runOnUiThread(() -> webView.evaluateJavascript("window." + function + "(" + safe + ")", null));
    }
    private void sendVoiceStatus(String message) { callJs("voiceStatus", message); }
    private void sendVoiceError(String message) { callJs("voiceError", message); }
    private void sendVoiceResult(String text) { callJs("receiveVoiceResult", text); }

    private final class VoiceBridge {
        @JavascriptInterface public void startVoiceRecognition() {
            runOnUiThread(() -> {
                if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                    pendingRecognition = true;
                    requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, MICROPHONE_PERMISSION_REQUEST);
                } else startListening();
            });
        }
    }

    @Override protected void onDestroy() {
        if (speechRecognizer != null) { speechRecognizer.destroy(); speechRecognizer = null; }
        if (webView != null) { webView.removeJavascriptInterface("AndroidVoice"); webView.destroy(); webView = null; }
        super.onDestroy();
    }
}
