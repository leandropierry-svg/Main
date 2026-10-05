# Meu Fluxo — projeto Android reconstruído

Aplicativo Android Studio para o APK `meu-fluxo.apk`, com package `br.com.meufluxo`, tela em WebView e registro por voz em português.

## Abrir e compilar

1. Instale Android Studio atual e um JDK compatível com Android Gradle Plugin 8.9.2 (JDK 17).
2. Abra esta pasta no Android Studio e aguarde a sincronização Gradle. Será necessário acesso à internet na primeira sincronização para baixar o Gradle/Android Gradle Plugin e o SDK Android API 35, caso ainda não estejam instalados.
3. Execute em um aparelho/emulador. Para voz, use aparelho com serviço de reconhecimento de fala configurado; aceite a permissão de microfone quando solicitado.

O projeto usa Gradle moderno e o Android Gradle Plugin 8.9.2. O wrapper não foi incluído porque não havia Gradle instalado na máquina de reconstrução para gerar os arquivos padrão; o Android Studio pode sincronizar o projeto com Gradle local/distribuição selecionada.

## O que foi recuperado e reconstruído

- **Recuperado diretamente do APK:** `app/src/main/assets/gestao-gastos.html` (15.466 bytes), com HTML, CSS e JavaScript original; `recovered/classes.dex` (7.708 bytes), preservado como evidência binária. O APK também continha Manifest binário e arquivos de assinatura, não incluídos no app reconstruído.
- **Inspecionado no DEX:** nomes e referências confirmam `br.com.meufluxo.MainActivity`, `VoiceBridge`, `AndroidVoice.startVoiceRecognition`, SpeechRecognizer, permissão `RECORD_AUDIO` e chamadas JavaScript `voiceStatus`, `voiceError` e `receiveVoiceResult`.
- **Reconstruído em Java:** `MainActivity.java`, ponte JS, WebView, pedido da permissão em tempo de execução e fluxo Android `SpeechRecognizer` com `pt-BR`. O arquivo Java original não estava presente no APK; não foi possível recuperar seu corpo exato sem decompilador, então esta implementação reproduz o comportamento identificado.
- **Reconstruído:** Manifest, tema, recursos e arquivos Gradle para um projeto Android Studio aberto/editável.

O APK não contém `.py`/`.pyc` conhecidos e a interface recuperada é HTML/CSS/JavaScript. Os arquivos de assinatura originais não foram reutilizados.
