# 📱 Flutter Deep Linking Entegrasyonu

Django web'den Flutter mobil app'e geçiş için deep linking kurulumu.

## 1. Bağımlılık Ekleme

```yaml
# pubspec.yaml
dependencies:
  uni_links: ^0.5.1
  app_links: ^3.4.5
```

## 2. Android Konfigürasyonu

### AndroidManifest.xml

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest>
    <application>
        <activity>
            <!-- Deep Link Scheme -->
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data
                    android:scheme="nakliyenet"
                    android:host="shipment" />
            </intent-filter>

            <!-- Universal Links -->
            <intent-filter android:autoVerify="true">
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data
                    android:scheme="https"
                    android:host="nakliyenet.com"
                    android:pathPrefix="/ilan/" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

## 3. iOS Konfigürasyonu

### Info.plist

```xml
<!-- ios/Runner/Info.plist -->
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleTypeRole</key>
        <string>Editor</string>
        <key>CFBundleURLName</key>
        <string>com.nakliyenet.app</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>nakliyenet</string>
        </array>
    </dict>
</array>

<!-- Universal Links -->
<key>com.apple.developer.associated-domains</key>
<array>
    <string>applinks:nakliyenet.com</string>
</array>
```

### apple-app-site-association (Django'da)

```json
// static/.well-known/apple-app-site-association
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "TEAM_ID.com.nakliyenet.app",
        "paths": ["/ilan/*"]
      }
    ]
  }
}
```

## 4. Flutter Kod Entegrasyonu

### main.dart

```dart
import 'package:uni_links/uni_links.dart';
import 'dart:async';

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  StreamSubscription? _sub;

  @override
  void initState() {
    super.initState();
    _handleIncomingLinks();
    _handleInitialLink();
  }

  /// Uygulama açıkken gelen linkler
  void _handleIncomingLinks() {
    _sub = uriLinkStream.listen((Uri? uri) {
      if (uri != null) {
        print('Incoming link: $uri');
        _navigateToDeepLink(uri);
      }
    }, onError: (err) {
      print('Deep link error: $err');
    });
  }

  /// Uygulama kapalıyken link ile açılma
  Future<void> _handleInitialLink() async {
    try {
      final uri = await getInitialUri();
      if (uri != null) {
        print('Initial link: $uri');
        _navigateToDeepLink(uri);
      }
    } catch (e) {
      print('Error getting initial link: $e');
    }
  }

  /// Deep link'e göre navigasyon
  void _navigateToDeepLink(Uri uri) {
    // nakliyenet://shipment/YN-2025-001234
    // veya https://nakliyenet.com/ilan/YN-2025-001234/

    if (uri.host == 'shipment' || uri.pathSegments.contains('ilan')) {
      // İlan numarasını çıkar
      final trackingNumber = uri.pathSegments.last.replaceAll('/', '');

      if (trackingNumber.isNotEmpty) {
        // İlan detay sayfasına git
        Navigator.of(context).pushNamed(
          '/shipment-detail',
          arguments: {'trackingNumber': trackingNumber},
        );
      }
    }
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NAKLIYE NET',
      // ... routes
      onGenerateRoute: (settings) {
        if (settings.name == '/shipment-detail') {
          final args = settings.arguments as Map<String, dynamic>;
          final trackingNumber = args['trackingNumber'] as String;

          return MaterialPageRoute(
            builder: (context) => ShipmentDetailView(
              trackingNumber: trackingNumber,
            ),
          );
        }
        return null;
      },
    );
  }
}
```

### ShipmentDetailView Değişikliği

```dart
class ShipmentDetailView extends StatefulWidget {
  final String? shipmentId;
  final String? trackingNumber; // YENİ!

  const ShipmentDetailView({
    Key? key,
    this.shipmentId,
    this.trackingNumber,
  }) : super(key: key);

  @override
  State<ShipmentDetailView> createState() => _ShipmentDetailViewState();
}

class _ShipmentDetailViewState extends State<ShipmentDetailView> {
  ShipmentModel? _shipment;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadShipment();
  }

  Future<void> _loadShipment() async {
    setState(() => _isLoading = true);

    try {
      ShipmentModel? shipment;

      if (widget.trackingNumber != null) {
        // Tracking number ile ara
        final allShipments = await _shipmentService.getAllShipments();
        shipment = allShipments.firstWhere(
          (s) => s.trackingNumber == widget.trackingNumber,
          orElse: () => null,
        );
      } else if (widget.shipmentId != null) {
        // Normal ID ile ara
        shipment = await _shipmentService.getShipmentById(widget.shipmentId!);
      }

      if (mounted) {
        setState(() {
          _shipment = shipment;
          _isLoading = false;
        });
      }
    } catch (e) {
      print('Error loading shipment: $e');
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Yükleniyor...')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_shipment == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('İlan Bulunamadı')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.grey),
              const SizedBox(height: 16),
              const Text('Bu ilan bulunamadı'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Geri Dön'),
              ),
            ],
          ),
        ),
      );
    }

    // Normal ilan detay UI
    return Scaffold(
      appBar: AppBar(
        title: Text(_shipment!.title),
      ),
      body: // ... mevcut UI
    );
  }
}
```

## 5. Test Etme

### Android

```bash
# Komut satırından test
adb shell am start -W -a android.intent.action.VIEW -d "nakliyenet://shipment/YN-2025-001234" com.nakliyenet.app

# Universal link test
adb shell am start -W -a android.intent.action.VIEW -d "https://nakliyenet.com/ilan/YN-2025-001234/" com.nakliyenet.app
```

### iOS

```bash
# Simulator'da test
xcrun simctl openurl booted "nakliyenet://shipment/YN-2025-001234"

# Universal link test
xcrun simctl openurl booted "https://nakliyenet.com/ilan/YN-2025-001234/"
```

## 6. Django Template'de Kullanım

```html
<!-- templates/website/ilan_detay.html -->

<!-- Custom Scheme Link -->
<a href="nakliyenet://shipment/{{ shipment.trackingNumber }}" class="btn btn-primary">
    <i class="bi bi-box-arrow-up-right me-2"></i>
    Uygulamada Aç
</a>

<!-- Universal Link (Fallback) -->
<a href="https://nakliyenet.com/ilan/{{ shipment.trackingNumber }}/" class="btn btn-secondary">
    İlanı Görüntüle
</a>

<!-- JavaScript ile Akıllı Yönlendirme -->
<button onclick="openInApp('{{ shipment.trackingNumber }}')" class="btn btn-primary">
    Uygulamada Aç
</button>

<script>
function openInApp(trackingNumber) {
    const deepLink = `nakliyenet://shipment/${trackingNumber}`;
    const fallbackUrl = `https://nakliyenet.com/ilan/${trackingNumber}/`;

    // Deep link'i dene
    window.location.href = deepLink;

    // 2 saniye sonra açılmadıysa fallback
    setTimeout(() => {
        if (confirm('Uygulama yüklü değil. App Store/Google Play\'e gitmek ister misiniz?')) {
            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
            const appUrl = isIOS
                ? '{{ IOS_APP_URL }}'
                : '{{ ANDROID_APP_URL }}';
            window.location.href = appUrl;
        }
    }, 2000);
}
</script>
```

## 7. URL Formatları

```
✅ Deep Link (Custom Scheme):
   nakliyenet://shipment/YN-2025-001234

✅ Universal Link (HTTPS):
   https://nakliyenet.com/ilan/YN-2025-001234/

✅ Web Fallback:
   https://nakliyenet.com/ilan/YN-2025-001234/
   → SEO friendly, crawlable
```

## 8. Debug

```dart
// main.dart - Debug için log ekleyin
void _navigateToDeepLink(Uri uri) {
    print('🔗 Deep Link Received:');
    print('  Scheme: ${uri.scheme}');
    print('  Host: ${uri.host}');
    print('  Path: ${uri.path}');
    print('  Segments: ${uri.pathSegments}');

    // ... navigation kodu
}
```

## ✅ Checklist

- [ ] `uni_links` paketi eklendi
- [ ] AndroidManifest.xml güncellendi
- [ ] Info.plist güncellendi
- [ ] `apple-app-site-association` dosyası oluşturuldu
- [ ] Deep link handler eklendi
- [ ] ShipmentDetailView tracking number desteği eklendi
- [ ] Django template'lerde deep link butonları eklendi
- [ ] Android'de test edildi
- [ ] iOS'ta test edildi

## 🎯 Sonuç

Artık Django web'den "Uygulamada Aç" butonuna tıklandığında:
1. Uygulama yüklüyse → Direkt ilan detaya gider
2. Uygulama yüklü değilse → App Store/Google Play'e yönlendirir
3. Web'de kalırsa → SEO-friendly sayfa görünür
