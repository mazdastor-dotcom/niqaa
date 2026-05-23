# نقاء

**نقاء** برنامج ويندوز محمول يركز على إزالة البرامج من جذورها، تنظيف المخلفات والكاش، مراقبة بدء التشغيل، وفحص السلوكيات المشبوهة محليًا. يعمل كملف واحد بدون تثبيت، ومناسب للمشاركة والاستخدام الشخصي على أجهزة Windows.

المطور: **ماجد السعدي**  
التواصل: [@iML7x على X](https://x.com/iML7x)  
جميع الحقوق محفوظة.

## لماذا نقاء؟

كثير من برامج الإزالة التقليدية تحذف التطبيق فقط وتترك خلفه مجلدات، كاش، مفاتيح Registry، عناصر بدء تشغيل، وسجلات قد تبقى لوقت طويل. نقاء يحاول جمع هذه المهام في أداة واحدة واضحة: إزالة، تنظيف، فحص، مراقبة، وتقرير.

## أبرز الفوائد

- تنظيف أعمق بعد إزالة البرامج بدل الاكتفاء بمزيل التثبيت الرسمي.
- عرض البرامج المثبتة مع الحجم، الناشر، الإصدار، تاريخ التثبيت، والمسار.
- ترتيب وبحث سريع حسب الاسم، الحجم، الناشر، الإصدار، وآخر تثبيت.
- فحص مخلفات البرامج وعزلها بدل حذفها مباشرة لتقليل المخاطر.
- استرجاع آخر عزل عند الحاجة.
- تنظيف كاش الجهاز من مسارات النظام والمتصفح والتطبيقات الشائعة.
- قناص بدء التشغيل مع تقييم خطورة تقني وشرح سبب التصنيف.
- فحص أمان محلي مبني على مؤشرات سلوكية مثل المسارات الخطرة، السكربتات المشبوهة، الاستدعاءات الحساسة، والـ entropy.
- مراقبة الاتصالات الحالية وربطها بالعمليات.
- مراقبة DNS Cache وسجلات Hosts وبعض آثار النظام المفيدة للفحص.
- مراقبة تثبيت البرامج عبر Snapshot قبل/بعد.
- تقرير صحة بنقرة واحدة يجمع أهم مؤشرات الجهاز.
- تحديث التطبيقات المثبتة عبر `winget` عند توفره على الجهاز.
- وضع شريط النظام: عند إغلاق النافذة يبقى نقاء بجانب الساعة مثل التطبيقات الاحترافية.
- تنبيهات أذكار وأدعية عشوائية تعمل أثناء وجود البرنامج في الخلفية.
- واجهة عربية بالكامل مع دعم الإنجليزية.
- نسخة محمولة بدون تثبيت.

## مميزات الواجهة

- تصميم داكن احترافي ومناسب للقراءة.
- واجهة مرنة تتكيف مع تكبير وتصغير النافذة.
- قوائم كلك يمين للبرامج والمخلفات.
- تفاصيل واضحة للبرنامج المحدد: الحجم، المسار، الناشر، الإصدار، وأمر الإزالة.
- زر تواصل مباشر يفتح حساب X للمطور.
- شريط أذكار ظاهر داخل التطبيق وتنبيهات أذكار اختيارية.

## ملاحظات الأمان

نقاء لا يدعي أنه مضاد فيروسات كامل ولا يستبدل حلول الحماية المتخصصة. فحص الأمان المحلي في نقاء يعتمد على مؤشرات وسلوكيات heuristics للمساعدة في اكتشاف العناصر التي تحتاج مراجعة، مثل عناصر بدء التشغيل الغريبة أو الملفات التنفيذية في مسارات غير معتادة أو السكربتات عالية الخطورة.

بعض عمليات الإزالة والتنظيف تحتاج صلاحيات مسؤول. البرنامج يستخدم العزل والاسترجاع لتقليل خطر الحذف الخاطئ، ومع ذلك يجب مراجعة النتائج قبل تنفيذ الحذف أو العزل.

## التشغيل

شغل الملف المحمول:

```powershell
.\نقاء.exe
```

للاستفادة من كل خصائص الإزالة العميقة وبدء التشغيل، يفضل تشغيله كمسؤول.

## البناء من المصدر

المتطلبات على جهاز المطور فقط:

- Python 3.12+
- PyInstaller
- Pillow لتوليد الأيقونة
- pywin32 لدعم أيقونة شريط النظام

توليد الأيقونة:

```powershell
python make_icon.py
```

بناء نسخة محمولة:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --icon ".\niqaa.ico" --name "نقاء" ".\root_uninstaller.py"
```

لبناء نسخة أصغر حجمًا بدون حذف أي ميزة، استخدم UPX أثناء البناء:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --upx-dir ".\tools\upx\upx-5.1.1-win64" --icon ".\niqaa.ico" --name "نقاء" ".\root_uninstaller.py"
```

الملف النهائي يظهر داخل:

```text
dist\نقاء.exe
```

---

# Niqaa

**Niqaa** is a portable Windows utility for deep application removal, leftover cleanup, cache cleaning, startup inspection, and local behavior-based security checks. It runs as a single executable with no installation required.

Developer: **Majed Alsaadi**  
Contact: [@iML7x on X](https://x.com/iML7x)  
All rights reserved.

## What Niqaa Provides

Traditional uninstallers often remove the main app while leaving folders, cache, Registry entries, startup items, and logs behind. Niqaa brings removal, cleanup, inspection, monitoring, and reporting into one focused tool.

## Key Benefits

- Deeper cleanup after uninstalling applications.
- Installed app list with size, publisher, version, install date, and path.
- Fast search and sorting by name, size, publisher, version, and install date.
- Leftover scanning with quarantine instead of direct deletion.
- Restore support for the latest quarantine operation.
- Device cache cleanup across system, browser, and common app locations.
- Startup Hunter with technical risk scoring and reason explanations.
- Local heuristic security scan for suspicious paths, scripts, imports, persistence, and entropy signals.
- Current connection monitoring mapped to processes.
- DNS cache and system trace inspection.
- Install Watcher snapshot before/after installation.
- One-click health report.
- App update discovery through `winget` when available.
- System tray mode: closing the window keeps Niqaa running near the clock.
- Random dhikr and dua notifications while running in the background.
- Arabic-first interface with English support.
- Portable, one-file executable.

## Security Notes

Niqaa is not a full antivirus replacement. Its security checks are local heuristics designed to highlight suspicious items that deserve review, such as unusual startup entries, executable files in risky locations, suspicious scripts, or persistence indicators.

Some cleanup and startup operations require administrator privileges. Niqaa uses quarantine and restore flows to reduce deletion risk, but results should still be reviewed before action.

## Run

```powershell
.\نقاء.exe
```

For deep uninstall and startup actions, run as administrator.

## Build From Source

Developer requirements:

- Python 3.12+
- PyInstaller
- Pillow
- pywin32

Generate icon:

```powershell
python make_icon.py
```

Build portable executable:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --icon ".\niqaa.ico" --name "نقاء" ".\root_uninstaller.py"
```

To build a smaller executable without removing features, use UPX during the PyInstaller build:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --upx-dir ".\tools\upx\upx-5.1.1-win64" --icon ".\niqaa.ico" --name "نقاء" ".\root_uninstaller.py"
```

Output:

```text
dist\نقاء.exe
```
