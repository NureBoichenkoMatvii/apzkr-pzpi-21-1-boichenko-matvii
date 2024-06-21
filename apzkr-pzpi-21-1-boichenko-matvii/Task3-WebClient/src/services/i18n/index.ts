import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import ukr from './locales/ukr.json';
import eng from './locales/eng.json';

i18n
  .use(initReactI18next)
  .init({
    fallbackLng: 'eng',
    load: 'languageOnly',
    supportedLngs: ['eng', 'ukr'],
    resources: {
      eng: {
        translation: eng
      },
      ukr: {
        translation: ukr
      }
    },
    interpolation: {
      escapeValue: false, // react already safes from xss
    },
  });

export default i18n;