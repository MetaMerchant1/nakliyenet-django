# Firebase Credentials Base64 Generator
$content = Get-Content firebase-adminsdk.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)

Write-Output "=== FIREBASE_CREDENTIALS_BASE64 ==="
Write-Output ""
Write-Output $base64
Write-Output ""
Write-Output "=== Uzunluk: $($base64.Length) karakter ==="
Write-Output ""
Write-Output "Bu metni kopyala ve Render'da Environment Variable olarak ekle!"
