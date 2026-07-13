/**
 * Central translation dictionary for the Mifos Loan Summarizer.
 *
 * Structure:  translations[languageCode][flatKey] = string
 * Supported languages: en (English), hi (Hindi), es (Spanish)
 *
 * Brand names (Mifos X, Fineract, WhatsApp) are intentionally left untranslated.
 */

const translations = {
  /* ------------------------------------------------------------------ */
  /*  ENGLISH                                                           */
  /* ------------------------------------------------------------------ */
  en: {
    // Header
    'header.title': 'Smart Contract & Loan Agreement Analyzer',
    'header.badge': 'THE MIFOS INITIATIVE',

    // Page hero
    'hero.eyebrow': 'Loan analysis',
    'hero.title': 'Understand your loan agreement',
    'hero.description':
      'Paste any loan contract, upload a document (PDF, DOCX, TXT) or scanned image, or select a Mifos X product to get a plain-language summary, extracted terms, and risk analysis.',

    // Tabs
    'tab.paste': 'Paste text',
    'tab.pdf': 'Upload document',
    'tab.mifos': 'Mifos X product',

    // Loading / status
    'status.analysing': 'Analysing contract…',

    // Contract input
    'contract.title': 'Paste loan agreement',
    'contract.charHint': '50 – 50,000 characters',
    'contract.placeholder': 'Paste the full text of a loan agreement here…',
    'contract.minWarning': ' — need at least 50',
    'contract.reset': 'Reset',
    'contract.submit': 'Analyse contract',
    'contract.submitting': 'Analysing…',

    // PDF upload
    'pdf.title': 'Upload document',
    'pdf.maxSize': 'Max 10 MB',
    'pdf.dropHere': 'Drop file here',
    'pdf.browse': 'Click to browse',
    'pdf.orDrag': ' or drag and drop',
    'pdf.typeHint': 'PDF, DOCX, TXT, or image (PNG/JPG) · Up to 10 MB',
    'pdf.removeFile': 'Remove file',
    'pdf.reset': 'Reset',
    'pdf.submit': 'Analyse document',
    'pdf.submitting': 'Analysing…',
    'pdf.noFile': 'No file selected.',
    'pdf.unsupported': 'Unsupported file type "{ext}". Accepted: PDF, DOCX, TXT, PNG, JPG',
    'pdf.empty': 'File is empty.',
    'pdf.tooLarge': 'File is too large ({size}). Maximum is 10 MB.',

    // Mifos product picker
    'mifos.title': 'Select Mifos X loan product',
    'mifos.refresh': '↻ Refresh',
    'mifos.refreshTitle': 'Clear cache and refresh products from Fineract',
    'mifos.subtitle': 'Pulls loan product data directly from Fineract API',
    'mifos.loading': 'Loading loan products…',
    'mifos.selectDefault': '— Select a loan product —',
    'mifos.productCount': '{count} product{s} available',
    'mifos.noProducts': 'No products found — try refreshing or check Fineract connection',
    'mifos.connectError': '⚠ Cannot connect to Mifos X',
    'mifos.retry': '↻ Retry',
    'mifos.clearRetry': '🗑 Clear cache & retry',

    // Results
    'results.title': 'Analysis results',
    'results.segments': '{n} segments',
    'results.tab.summary': 'Summary',
    'results.tab.entities': 'Entities',
    'results.tab.risk': 'Risk',
    'results.tab.rawJson': 'Raw JSON',

    // Stats
    'stat.loanAmount': 'Loan amount',
    'stat.interestRate': 'Interest rate',
    'stat.monthlyEmi': 'Monthly EMI',
    'stat.totalRepayment': 'Total repayment',
    'stat.perAnnum': 'per annum',
    'stat.months': '{n} months',
    'stat.interest': '{amount} interest',

    // Math check
    'math.label': 'Math Check',
    'math.monthlyEmi': 'Monthly EMI:',
    'math.tenure': 'Loan Tenure:',
    'math.tenureMonths': '{n} months',
    'math.calcTotal': 'Calculated Total:',
    'math.contractStates': 'Contract States:',
    'math.difference': '{pct}% difference',

    // Risk
    'risk.bpsLabel': 'Borrower Protection Score',
    'risk.lowProtection': 'Low Protection',
    'risk.moderateProtection': 'Moderate Protection',
    'risk.highProtection': 'High Protection',
    'risk.primaryIssue': 'Primary issue:',
    'risk.negotiationTips': 'Negotiation Tips:',
    'risk.scoreLabel': 'Risk score',
    'risk.noFactors': 'No significant risk factors detected.',
    'risk.defaultTriggers': 'Default triggers',

    // Entity card
    'entity.verified': '🟢 Verified',
    'entity.needsReview': '🟡 Needs Review',
    'entity.uncertain': '🔴 Uncertain',
    'entity.hideSource': 'Hide source ↑',
    'entity.showSource': 'Source ↓',

    // Export
    'export.label': 'WhatsApp / SMS',
    'export.copied': '✓ Copied!',
    'export.copy': '⎘ Copy',

    // Error fallback (full page)
    'error.title': 'Something went wrong',
    'error.description':
      "We're sorry, but something unexpected happened. This error has been logged and we'll look into it. Please try again or refresh the page.",
    'error.tryAgain': 'Try Again',
    'error.refreshPage': 'Refresh Page',
    'error.details': 'Error Details (Development Only)',
    'error.message': 'Error Message:',
    'error.stack': 'Stack Trace:',
    'error.componentStack': 'Component Stack:',
    'error.helpText':
      'If this problem persists, please contact support or ',
    'error.reportIssue': 'report an issue',

    // Section error fallback
    'sectionError.title': 'This section encountered an error',
    'sectionError.description':
      'Something went wrong while loading this section. The rest of the app should still work normally.',
    'sectionError.tryAgain': 'Try Again',
    'sectionError.details': 'Error Details (Development Only)',
  },

  /* ------------------------------------------------------------------ */
  /*  HINDI                                                             */
  /* ------------------------------------------------------------------ */
  hi: {
    // Header
    'header.title': 'स्मार्ट अनुबंध और ऋण समझौता विश्लेषक',
    'header.badge': 'द मिफ़ोस इनिशिएटिव',

    // Page hero
    'hero.eyebrow': 'ऋण विश्लेषण',
    'hero.title': 'अपने ऋण समझौते को समझें',
    'hero.description':
      'कोई भी ऋण अनुबंध चिपकाएँ, दस्तावेज़ (PDF, DOCX, TXT) या स्कैन की गई छवि अपलोड करें, या Mifos X उत्पाद चुनें — सरल भाषा में सारांश, निकाली गई शर्तें और जोखिम विश्लेषण प्राप्त करें।',

    // Tabs
    'tab.paste': 'टेक्स्ट चिपकाएँ',
    'tab.pdf': 'दस्तावेज़ अपलोड करें',
    'tab.mifos': 'Mifos X उत्पाद',

    // Loading / status
    'status.analysing': 'अनुबंध का विश्लेषण हो रहा है…',

    // Contract input
    'contract.title': 'ऋण समझौता चिपकाएँ',
    'contract.charHint': '50 – 50,000 अक्षर',
    'contract.placeholder': 'ऋण समझौते का पूरा पाठ यहाँ चिपकाएँ…',
    'contract.minWarning': ' — कम से कम 50 चाहिए',
    'contract.reset': 'रीसेट',
    'contract.submit': 'अनुबंध का विश्लेषण करें',
    'contract.submitting': 'विश्लेषण हो रहा है…',

    // PDF upload
    'pdf.title': 'दस्तावेज़ अपलोड करें',
    'pdf.maxSize': 'अधिकतम 10 MB',
    'pdf.dropHere': 'फ़ाइल यहाँ छोड़ें',
    'pdf.browse': 'ब्राउज़ करें',
    'pdf.orDrag': ' या खींचकर छोड़ें',
    'pdf.typeHint': 'PDF, DOCX, TXT, या छवि (PNG/JPG) · अधिकतम 10 MB',
    'pdf.removeFile': 'फ़ाइल हटाएँ',
    'pdf.reset': 'रीसेट',
    'pdf.submit': 'दस्तावेज़ का विश्लेषण करें',
    'pdf.submitting': 'विश्लेषण हो रहा है…',
    'pdf.noFile': 'कोई फ़ाइल चयनित नहीं।',
    'pdf.unsupported': 'असमर्थित फ़ाइल प्रकार "{ext}"। स्वीकृत: PDF, DOCX, TXT, PNG, JPG',
    'pdf.empty': 'फ़ाइल खाली है।',
    'pdf.tooLarge': 'फ़ाइल बहुत बड़ी है ({size})। अधिकतम 10 MB।',

    // Mifos product picker
    'mifos.title': 'Mifos X ऋण उत्पाद चुनें',
    'mifos.refresh': '↻ रीफ़्रेश',
    'mifos.refreshTitle': 'कैश साफ़ करें और Fineract से उत्पाद रीफ़्रेश करें',
    'mifos.subtitle': 'Fineract API से सीधे ऋण उत्पाद डेटा लाता है',
    'mifos.loading': 'ऋण उत्पाद लोड हो रहे हैं…',
    'mifos.selectDefault': '— ऋण उत्पाद चुनें —',
    'mifos.productCount': '{count} उत्पाद उपलब्ध',
    'mifos.noProducts': 'कोई उत्पाद नहीं मिला — रीफ़्रेश करें या Fineract कनेक्शन जाँचें',
    'mifos.connectError': '⚠ Mifos X से कनेक्ट नहीं हो पा रहा',
    'mifos.retry': '↻ पुनः प्रयास',
    'mifos.clearRetry': '🗑 कैश साफ़ करें और पुनः प्रयास',

    // Results
    'results.title': 'विश्लेषण परिणाम',
    'results.segments': '{n} खंड',
    'results.tab.summary': 'सारांश',
    'results.tab.entities': 'संस्थाएँ',
    'results.tab.risk': 'जोखिम',
    'results.tab.rawJson': 'Raw JSON',

    // Stats
    'stat.loanAmount': 'ऋण राशि',
    'stat.interestRate': 'ब्याज दर',
    'stat.monthlyEmi': 'मासिक EMI',
    'stat.totalRepayment': 'कुल भुगतान',
    'stat.perAnnum': 'प्रति वर्ष',
    'stat.months': '{n} महीने',
    'stat.interest': '{amount} ब्याज',

    // Math check
    'math.label': 'गणित जाँच',
    'math.monthlyEmi': 'मासिक EMI:',
    'math.tenure': 'ऋण अवधि:',
    'math.tenureMonths': '{n} महीने',
    'math.calcTotal': 'गणना किया गया कुल:',
    'math.contractStates': 'अनुबंध बताता है:',
    'math.difference': '{pct}% अंतर',

    // Risk
    'risk.bpsLabel': 'उधारकर्ता सुरक्षा स्कोर',
    'risk.lowProtection': 'कम सुरक्षा',
    'risk.moderateProtection': 'मध्यम सुरक्षा',
    'risk.highProtection': 'उच्च सुरक्षा',
    'risk.primaryIssue': 'मुख्य मुद्दा:',
    'risk.negotiationTips': 'बातचीत के सुझाव:',
    'risk.scoreLabel': 'जोखिम स्कोर',
    'risk.noFactors': 'कोई महत्वपूर्ण जोखिम कारक नहीं पाए गए।',
    'risk.defaultTriggers': 'डिफ़ॉल्ट ट्रिगर',

    // Entity card
    'entity.verified': '🟢 सत्यापित',
    'entity.needsReview': '🟡 समीक्षा आवश्यक',
    'entity.uncertain': '🔴 अनिश्चित',
    'entity.hideSource': 'स्रोत छिपाएँ ↑',
    'entity.showSource': 'स्रोत ↓',

    // Export
    'export.label': 'WhatsApp / SMS',
    'export.copied': '✓ कॉपी हो गया!',
    'export.copy': '⎘ कॉपी',

    // Error fallback (full page)
    'error.title': 'कुछ गलत हो गया',
    'error.description':
      'हमें खेद है, लेकिन कुछ अप्रत्याशित हुआ। यह त्रुटि लॉग हो गई है। कृपया पुनः प्रयास करें या पेज रीफ़्रेश करें।',
    'error.tryAgain': 'पुनः प्रयास करें',
    'error.refreshPage': 'पेज रीफ़्रेश करें',
    'error.details': 'त्रुटि विवरण (केवल विकास)',
    'error.message': 'त्रुटि संदेश:',
    'error.stack': 'स्टैक ट्रेस:',
    'error.componentStack': 'कंपोनेंट स्टैक:',
    'error.helpText':
      'यदि यह समस्या बनी रहती है, तो कृपया सहायता से संपर्क करें या ',
    'error.reportIssue': 'समस्या की रिपोर्ट करें',

    // Section error fallback
    'sectionError.title': 'इस अनुभाग में त्रुटि हुई',
    'sectionError.description':
      'इस अनुभाग को लोड करते समय कुछ गलत हो गया। बाकी ऐप सामान्य रूप से काम करना चाहिए।',
    'sectionError.tryAgain': 'पुनः प्रयास करें',
    'sectionError.details': 'त्रुटि विवरण (केवल विकास)',
  },

  /* ------------------------------------------------------------------ */
  /*  SPANISH                                                           */
  /* ------------------------------------------------------------------ */
  es: {
    // Header
    'header.title': 'Analizador de Contratos y Préstamos',
    'header.badge': 'LA INICIATIVA MIFOS',

    // Page hero
    'hero.eyebrow': 'Análisis de préstamos',
    'hero.title': 'Comprende tu contrato de préstamo',
    'hero.description':
      'Pega cualquier contrato de préstamo, sube un documento (PDF, DOCX, TXT) o imagen escaneada, o selecciona un producto Mifos X para obtener un resumen en lenguaje sencillo, términos extraídos y análisis de riesgos.',

    // Tabs
    'tab.paste': 'Pegar texto',
    'tab.pdf': 'Subir documento',
    'tab.mifos': 'Producto Mifos X',

    // Loading / status
    'status.analysing': 'Analizando contrato…',

    // Contract input
    'contract.title': 'Pegar contrato de préstamo',
    'contract.charHint': '50 – 50.000 caracteres',
    'contract.placeholder': 'Pega el texto completo del contrato de préstamo aquí…',
    'contract.minWarning': ' — se necesitan al menos 50',
    'contract.reset': 'Restablecer',
    'contract.submit': 'Analizar contrato',
    'contract.submitting': 'Analizando…',

    // PDF upload
    'pdf.title': 'Subir documento',
    'pdf.maxSize': 'Máx. 10 MB',
    'pdf.dropHere': 'Suelta el archivo aquí',
    'pdf.browse': 'Haz clic para buscar',
    'pdf.orDrag': ' o arrastra y suelta',
    'pdf.typeHint': 'PDF, DOCX, TXT o imagen (PNG/JPG) · Hasta 10 MB',
    'pdf.removeFile': 'Eliminar archivo',
    'pdf.reset': 'Restablecer',
    'pdf.submit': 'Analizar documento',
    'pdf.submitting': 'Analizando…',
    'pdf.noFile': 'No se ha seleccionado ningún archivo.',
    'pdf.unsupported': 'Tipo de archivo no admitido "{ext}". Aceptados: PDF, DOCX, TXT, PNG, JPG',
    'pdf.empty': 'El archivo está vacío.',
    'pdf.tooLarge': 'El archivo es demasiado grande ({size}). Máximo 10 MB.',

    // Mifos product picker
    'mifos.title': 'Seleccionar producto de préstamo Mifos X',
    'mifos.refresh': '↻ Actualizar',
    'mifos.refreshTitle': 'Limpiar caché y actualizar productos de Fineract',
    'mifos.subtitle': 'Obtiene datos de productos directamente de la API de Fineract',
    'mifos.loading': 'Cargando productos de préstamo…',
    'mifos.selectDefault': '— Selecciona un producto —',
    'mifos.productCount': '{count} producto{s} disponible{s}',
    'mifos.noProducts': 'No se encontraron productos — intenta actualizar o verifica la conexión con Fineract',
    'mifos.connectError': '⚠ No se puede conectar a Mifos X',
    'mifos.retry': '↻ Reintentar',
    'mifos.clearRetry': '🗑 Limpiar caché y reintentar',

    // Results
    'results.title': 'Resultados del análisis',
    'results.segments': '{n} segmentos',
    'results.tab.summary': 'Resumen',
    'results.tab.entities': 'Entidades',
    'results.tab.risk': 'Riesgo',
    'results.tab.rawJson': 'JSON crudo',

    // Stats
    'stat.loanAmount': 'Monto del préstamo',
    'stat.interestRate': 'Tasa de interés',
    'stat.monthlyEmi': 'Cuota mensual',
    'stat.totalRepayment': 'Pago total',
    'stat.perAnnum': 'por año',
    'stat.months': '{n} meses',
    'stat.interest': '{amount} intereses',

    // Math check
    'math.label': 'Verificación matemática',
    'math.monthlyEmi': 'Cuota mensual:',
    'math.tenure': 'Plazo del préstamo:',
    'math.tenureMonths': '{n} meses',
    'math.calcTotal': 'Total calculado:',
    'math.contractStates': 'El contrato indica:',
    'math.difference': '{pct}% de diferencia',

    // Risk
    'risk.bpsLabel': 'Puntuación de protección al prestatario',
    'risk.lowProtection': 'Protección baja',
    'risk.moderateProtection': 'Protección moderada',
    'risk.highProtection': 'Protección alta',
    'risk.primaryIssue': 'Problema principal:',
    'risk.negotiationTips': 'Consejos de negociación:',
    'risk.scoreLabel': 'Puntuación de riesgo',
    'risk.noFactors': 'No se detectaron factores de riesgo significativos.',
    'risk.defaultTriggers': 'Disparadores de incumplimiento',

    // Entity card
    'entity.verified': '🟢 Verificado',
    'entity.needsReview': '🟡 Necesita revisión',
    'entity.uncertain': '🔴 Incierto',
    'entity.hideSource': 'Ocultar fuente ↑',
    'entity.showSource': 'Fuente ↓',

    // Export
    'export.label': 'WhatsApp / SMS',
    'export.copied': '✓ ¡Copiado!',
    'export.copy': '⎘ Copiar',

    // Error fallback (full page)
    'error.title': 'Algo salió mal',
    'error.description':
      'Lo sentimos, pero ocurrió algo inesperado. Este error ha sido registrado. Por favor, inténtalo de nuevo o actualiza la página.',
    'error.tryAgain': 'Intentar de nuevo',
    'error.refreshPage': 'Actualizar página',
    'error.details': 'Detalles del error (solo desarrollo)',
    'error.message': 'Mensaje de error:',
    'error.stack': 'Traza de pila:',
    'error.componentStack': 'Pila de componentes:',
    'error.helpText':
      'Si este problema persiste, contacta a soporte o ',
    'error.reportIssue': 'reporta un problema',

    // Section error fallback
    'sectionError.title': 'Esta sección encontró un error',
    'sectionError.description':
      'Algo salió mal al cargar esta sección. El resto de la aplicación debería seguir funcionando normalmente.',
    'sectionError.tryAgain': 'Intentar de nuevo',
    'sectionError.details': 'Detalles del error (solo desarrollo)',
  },
}

export default translations
