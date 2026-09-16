// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Arabic (`ar`).
class AppLocalizationsAr extends AppLocalizations {
  AppLocalizationsAr([String locale = 'ar']) : super(locale);

  @override
  String get appTitle => 'كرة القدم المباشرة بالذكاء الاصطناعي';

  @override
  String get live => 'مباشر';

  @override
  String get allMatches => 'جميع المباريات';

  @override
  String get leagues => 'البطولات';

  @override
  String get matchDetail => 'تفاصيل المباراة';

  @override
  String get events => 'الأحداث';

  @override
  String get statistics => 'الإحصائيات';

  @override
  String get aiAnalysis => 'تحليل الذكاء الاصطناعي';

  @override
  String get streamUnavailable => 'لا يوجد بث مصرح به';

  @override
  String get loading => 'جاري التحميل...';

  @override
  String get loadingLiveMatches => 'جاري تحميل المباريات المباشرة...';

  @override
  String get loadingMatches => 'جاري تحميل المباريات...';

  @override
  String get loadingLeagues => 'جاري تحميل البطولات...';

  @override
  String get loadingMatch => 'جاري تحميل المباراة...';

  @override
  String get noLiveMatches => 'لا توجد مباريات مباشرة في الوقت الحالي';

  @override
  String get noMatches => 'لا توجد مباريات متاحة';

  @override
  String get noLeagues => 'لا توجد بطولات متاحة';

  @override
  String get matchNotFound => 'المباراة غير موجودة';

  @override
  String get retry => 'إعادة المحاولة';

  @override
  String get verified => 'تم التحقق';

  @override
  String get vs => 'ضد';

  @override
  String get unknown => 'غير معروف';

  @override
  String assistedBy(Object player) {
    return 'ركلة حاسمة: $player';
  }

  @override
  String get highValidation => 'ثقة عالية';

  @override
  String get partialValidation => 'ثقة جزئية';

  @override
  String get lowValidation => 'ثقة منخفضة';

  @override
  String get pullToRefresh => 'اسحب للتحديث';

  @override
  String get networkError => 'خطأ في الشبكة. يرجى التحقق من اتصالك.';

  @override
  String get serverError => 'خطأ في الخادم. يرجى المحاولة مرة أخرى لاحقاً.';

  @override
  String get homeTeam => 'المضيف';

  @override
  String get awayTeam => 'الضيف';
}
