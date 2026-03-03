// Conditional export: použije web_download_web.dart na webe, inak web_download_stub.dart
export 'web_download_stub.dart'
    if (dart.library.html) 'web_download_web.dart';
