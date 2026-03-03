// Web implementation
import 'dart:html' as html;
import 'dart:convert';

void downloadFile(String text, String filename) {
  final bytes = utf8.encode(text);
  final blob = html.Blob([bytes], 'text/plain');
  final url = html.Url.createObjectUrlFromBlob(blob);

  final a = html.AnchorElement(href: url)
    ..download = filename
    ..click();

  html.Url.revokeObjectUrl(url);
}
