// Remember that the grammar name must match the filename
grammar DateAndTime;

@header {
from DateEnum import DateEnum
}

@parser::members {
    self.results = list()
}

value
    @init {
    }
        : (date_or_time)* EOF
        ;
/*
    HIGHEST LEVEL RULES
*/
date_or_time
    @init {
result = dict()
    }
    // durante i prossimi 10 giorni
    : day_duration
        {
result['type'] = DateEnum.TIMEX_DATE_DURATION;
result['value'] = $day_duration.s;
self.results.append(result);
        }
    // durante le prossime 10 settimane
    | week_duration
        {
result['type'] = DateEnum.TIMEX_DATE_DURATION;
result['value'] = $week_duration.s;
self.results.append(result);
        }
    // durante i prossimi 10 mesi
    | month_duration
        {
result['type'] = DateEnum.TIMEX_DATE_DURATION;
result['value'] = $month_duration.s;
self.results.append(result);
        }
    // durante i prossimi 10 anni
    | year_duration
        {
result['type'] = DateEnum.TIMEX_DATE_DURATION;
result['value'] = $year_duration.s;
self.results.append(result);
        }
    // primo lunedì di novembre
    | PRIMO day_absolute DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
       }
    // secondo lunedì di novembre
    | SECONDO day_absolute DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:2\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
          }
    // terzo lunedì di novembre
    | TERZO day_absolute DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:3\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
          }
    // quarto lunedì di novembre
    | QUARTO day_absolute DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:4\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
          }
    // quinto lunedì di novembre
    | QUINTO day_absolute DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:5\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
          }
    // ultimo lunedì di novembre
    | ULTIMO day_absolute DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:-1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
          }
    // prima domenica di novembre
    | PRIMA DOMENICA DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
        }
    // seconda domenica di novembre
    | SECONDA DOMENICA DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:2\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
        }
    // terza domenica di novembre
    | TERZA DOMENICA DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:3\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
        }
    // quarta domenica di novembre
    | QUARTA DOMENICA DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:4\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
        }
    // quinta domenica di novembre
    | QUINTA DOMENICA DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:5\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
        }
    // ultima domenica di novembre
    | ULTIMA DOMENICA DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$weekday_number:-1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
        }
    // prima (settimana) di novembre
    | PRIMA maybesettimana DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week_number:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
       }
    // seconda (settimana) di novembre
    | SECONDA maybesettimana DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week_number:2\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
        }
    // terza (settimana) di novembre
    | TERZA maybesettimana DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week_number:3\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
          }
    // quarta (settimana) di novembre
    | QUARTA maybesettimana DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week_number:4\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
          }
    // quinta (settimana) di novembre
    | QUINTA maybesettimana DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week_number:5\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
          }
    // ultima (settimana) di novembre
    | ULTIMA maybesettimana DI month
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week_number:-1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_";
self.results.append(result);
          }
    // seconda settimana, settimana 8
    | week_number
        {
result['type'] = DateEnum.TIMEX_WEEK;
result['value'] = "%d" % ($week_number.i);
self.results.append(result);
        }

    /*
     * WEEK DAYS
     */
    // scorso giovedi
    | SCORSO day_absolute
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:-1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
        }
  // prossimo giovedi, prossimo weekend
    | PROSSIMO day_absolute
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
       }
  // prossima domenica
    | PROSSIMA DOMENICA
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
       }
    // questo giovedi
    | QUESTO day_absolute
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:0\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
       }
    // giovedi prossimo
    | day_absolute PROSSIMO
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
        }
    // giovedi scorso
    | day_absolute SCORSO
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:-1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
       }
    // giovedi precedente
    | day_absolute PRECEDENTE
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:-1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
       }
    // venerdi mattina
    | day_absolute MATTINA
  {
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "\$morning\$";
self.results.append(result);
     }
    /*
     * RELATIVE DAYS
     */
    // ieri mattina
    | day_relative MATTINA
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $day_relative.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "\$morning\$";
self.results.append(result);
     }
    // prossimo novembre
    | PROSSIMO month
      {
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = "\$year:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_" ;
self.results.append(result);
        }
    // questo novembre
    | QUESTO month
      {
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = "\$year:0\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_" ;
self.results.append(result);
       }
    // scorso novembre
    | SCORSO month
      {
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = "\$year:-1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_" ;
self.results.append(result);
       }
    // novembre prossimo
    | month PROSSIMO
      {
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = "\$year:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_" ;
self.results.append(result);
        }
    // novembre scorso
    | month SCORSO
      {
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = "\$year:-1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "%02d" % ($month.i) + ":_" ;
self.results.append(result);
        }
    // 16/11/2013
    | date SLASH YEARNUM
    {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $date.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = $YEARNUM.text;
self.results.append(result);
    }
    // 16 novembre 2013
    | date YEARNUM
    {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $date.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = $YEARNUM.text;
self.results.append(result);
    }
    // ultimi 5 minuti
    | ULTIMI timecomponents
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "-:" + $timecomponents.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = $timecomponents.s;
self.results.append(result);
       }
    // scorsi 5 minuti
    | SCORSI timecomponents
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "-:" + $timecomponents.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = $timecomponents.s;
self.results.append(result);
       }
    // entro 5 minuti
    | ENTRO timecomponents
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "\$now\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = $timecomponents.s;
self.results.append(result);
       }
    // prossimi 5 minuti
    | PROSSIMI timecomponents
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "\$now\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = $timecomponents.s;
self.results.append(result);
       }
    // questi 5 minuti
    | QUESTI timecomponents
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "\$now\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = $timecomponents.s;
self.results.append(result);
       }
    // 5 minuti precedenti
    | timecomponents PRECEDENTI
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "-:" + $timecomponents.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = $timecomponents.s;
self.results.append(result);
        }
    | QUEST ORA
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "\$now\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = "01:_:_" ;
self.results.append(result);
       }
    | QUESTO MINUTO
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "\$now\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = "_:01:_" ;
self.results.append(result);
       }
    | QUESTO SECONDO
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = "\$now\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = "_:_:01" ;
self.results.append(result);
       }

    | DALLE a=number ALLE b=number
      {
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = (String.format("%02d",$a.i) + ":_:_") ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = (String.format("%02d",($b.i-$a.i)) + ":_:_") ;
self.results.append(result);
       }
    // fra le 3 e le 5
    | FRA LE a=number E LE b=number
      {
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = (String.format("%02d",$a.i) + ":_:_") ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = (String.format("%02d",($b.i-$a.i)) + ":_:_") ;
self.results.append(result);
       }
   | QUESTO POMERIGGIO
   {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$today\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "\$afternoon\$" ;
self.results.append(result);
      }
   | STASERA
   {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$today\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "\$evening\$" ;
self.results.append(result);
      }
  | STANOTTE
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$today\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "\$night\$" ;
self.results.append(result);
     }
    // tutti i giovedi
    | TUTTI I day_absolute
      {
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_REPEAT_TIME;
result['value'] = "\$weekly\$" ;
self.results.append(result);
       }
    // TODO need to split in 2 sub-rules
    // ogni sera
    | OGNI time_relative
      {
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = $time_relative.s ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_REPEAT_TIME;
result['value'] = "\$daily\$" ;
self.results.append(result);
       }
    // ogni mercoledi mattina
    | OGNI day_absolute MATTINA
      {
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_REPEAT_TIME;
result['value'] = "\$weekly\$" ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "\$morning\$" ;
self.results.append(result);
       }
     // ogni mercoledi
    | OGNI day_absolute
      {
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_REPEAT_TIME;
result['value'] = "\$weekly\$" ;
self.results.append(result);
       }
    | UN QUARTO A MEZZOGIORNO
      {
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "11:45:_" ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "\$morning\$" ;
self.results.append(result);
       }
    | MEZZOGIORNO MENO UN QUARTO
      {
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "11:45:_" ;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = "\$morning\$" ;
self.results.append(result);
       }
    | FRA UN LUNEDI
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$monday\$";
self.results.append(result);
      }
    | FRA UN MARTEDI
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$tuesday\$";
self.results.append(result);
      }
    | FRA UN MERCOLEDI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$wednesday\$";
self.results.append(result);
      }
    | FRA UN GIOVEDI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$thursday\$";
self.results.append(result);
      }
    | FRA UN VENERDI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$friday\$";
self.results.append(result);
      }
    | FRA UN SABATO
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$saturday\$";
self.results.append(result);
      }
    | FRA UNA DOMENICA
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
      }
    | FRA number LUNEDI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$monday\$";
self.results.append(result);
      }
    | FRA number MARTEDI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$tuesday\$";
self.results.append(result);
      }
    | FRA number MERCOLEDI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$wednesday\$";
self.results.append(result);
      }
    | FRA number GIOVEDI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$thursday\$";
self.results.append(result);
      }
    | FRA number VENERDI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$friday\$";
self.results.append(result);
      }
    | FRA number SABATI
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$saturday\$";
self.results.append(result);
      }
    | FRA number SABATO
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$saturday\$";
self.results.append(result);
      }
    | FRA number DOMENICHE
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
      }
    | FRA number DOMENICA
  {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:" + $number.i + "\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
      }
    | DOMENICA PROSSIMA
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = "\$week:1\$";
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = "\$sunday\$";
self.results.append(result);
          }
    // prossima stagione
    | season_relative
      {
result['type'] = DateEnum.TIMEX_SEASON;
result['value'] = $season_relative.s;
self.results.append(result);
          }
    /* WARNING the following rule may parse weird dates */
    // da ieri a dopodomani
    | DA x=day_relative A y=day_relative
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $x.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_END_DATE;
result['value'] = $y.s;
self.results.append(result);
            }
    // da settimana scorsa a fra 2 settimane
    | DA m=week_relative A n=week_relative
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $m.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_END_DATE;
result['value'] = $n.s;
self.results.append(result);
            }
    // da 2 mesi fa a fra 6 mesi
    | DA o=month_relative A p=month_relative
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $o.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_END_DATE;
result['value'] = $p.s;
self.results.append(result);
            }
    // da 7 anni fa a fra 4 anni
    | DA q=year_relative A r=year_relative
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $q.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_END_DATE;
result['value'] = $r.s;
self.results.append(result);
            }
    // 3 giorni fa, dopodomani
    | day_relative
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $day_relative.s;
self.results.append(result);
          }
    // 2 settimane fa, settimana prossima
    | week_relative
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $week_relative.s;
self.results.append(result);
          }
    // 2 mesi fa, mese prossimo
    | month_relative
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $month_relative.s;
self.results.append(result);
            }
    // 2 anni fa, anno prossimo
    | year_relative
      {
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = $year_relative.s;
self.results.append(result);
            }
    // per 5 minuti
    | duration
      {
result['type'] = DateEnum.TIMEX_DURATION;
result['value'] = $duration.s;
self.results.append(result);
      }
    // da 5 minuti fa a fra 5 minuti
    | DA s=rel_time_start A t=rel_time_start
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = $s.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_END_TIME;
result['value'] = $t.s;
self.results.append(result);
      }
    // dopo 5 minuti
    | rel_time_start
      {
result['type'] = DateEnum.TIMEX_REL_START_TIME;
result['value'] = $rel_time_start.s;
self.results.append(result);
      }
    // 5 minuti fa, fra 5 minuti
    | time_relative
      {
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = $time_relative.s;
self.results.append(result);
      }
    // tutti i giovedi
    | date_repeat
      {
result['type'] = DateEnum.TIMEX_REPEAT_TIME;
result['value'] = $date_repeat.s;
self.results.append(result);
      }
    // dal 16 novembre al 4 gennaio
    | DAL u=date AL v=date
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $u.s;
self.results.append(result);
result = dict()
result['type'] = DateEnum.TIMEX_END_DATE;
result['value'] = $v.s;
self.results.append(result);
            }
    // 16 novembre
    | date
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $date.s;
self.results.append(result);
      }
    // alle 5
  | time_start
  {
result['type'] = DateEnum.TIMEX_START_TIME;
result['value'] = $time_start.s;
self.results.append(result);
  }
    // 2013
    | year
      {
result['type'] = DateEnum.TIMEX_YEAR;
result['value'] = $year.s;
self.results.append(result);
      }
    // giovedi
    | day_absolute
      {
result['type'] = DateEnum.TIMEX_WEEKDAY;
result['value'] = $day_absolute.s;
self.results.append(result);
      }
    // natale
    | holiday
      {
result['type'] = DateEnum.TIMEX_DATE;
result['value'] = $holiday.s;
self.results.append(result);
      }
    // estate
    | season
      {
result['type'] = DateEnum.TIMEX_SEASON;
result['value'] = $season.s;
self.results.append(result);
      }
    ;

/*
    BEGIN 
    lower level rules
*/
day_duration returns [String s]
    /* Future */
    : DURANTE I PROSSIMI number GIORNI
        {$s = "\$day:" + $number.i + "\$"; }
    | DURANTE I number GIORNI PROSSIMI
        {$s = "\$day:" + $number.i + "\$"; }
    | DURANTE I number PROSSIMI GIORNI
        {$s = "\$day:" + $number.i + "\$"; }
    | NEL CORSO DEI PROSSIMI number GIORNI
        {$s = "\$day:" + $number.i + "\$"; }
    | NEL CORSO DEI number GIORNI PROSSIMI
        {$s = "\$day:" + $number.i + "\$"; }
    | NEL CORSO DEI number PROSSIMI GIORNI
        {$s = "\$day:" + $number.i + "\$"; }
    | PER I PROSSIMI number GIORNI
        {$s = "\$day:" + $number.i + "\$"; }
    | PER I number GIORNI PROSSIMI
        {$s = "\$day:" + $number.i + "\$"; }
    | PER I number PROSSIMI GIORNI
        {$s = "\$day:" + $number.i + "\$"; }
    /* Past */
    | DURANTE GLI SCORSI number GIORNI
        {$s = "\$day:-" + $number.i + "\$"; }
    | DURANTE I number GIORNI SCORSI
        {$s = "\$day:-" + $number.i + "\$"; }
    | DURANTE I number SCORSI GIORNI
        {$s = "\$day:-" + $number.i + "\$"; }
    | DURANTE I PASSATI number GIORNI
        {$s = "\$day:-" + $number.i + "\$"; }
    | DURANTE I number GIORNI PASSATI
        {$s = "\$day:-" + $number.i + "\$"; }
    | NEL CORSO DEGLI SCORSI number GIORNI
        {$s = "\$day:-" + $number.i + "\$"; }
    | NEL CORSO DEI number GIORNI SCORSI
        {$s = "\$day:-" + $number.i + "\$"; }
    | NEL CORSO DEI number SCORSI GIORNI
        {$s = "\$day:-" + $number.i + "\$"; }
    | NEL CORSO DEI number GIORNI PASSATI
        {$s = "\$day:-" + $number.i + "\$"; }
    | NEL CORSO DEI PASSATI number GIORNI
        {$s = "\$day:-" + $number.i + "\$"; }
    ;

week_duration returns [String s]
    /* Future */
    : DURANTE LA PROSSIMA SETTIMANA
        {$s = "\$week:1\$"; }
    | DURANTE LA SETTIMANA PROSSIMA
        {$s = "\$week:1\$"; }
    | DURANTE SETTIMANA PROSSIMA
        {$s = "\$week:1\$"; }
    | DURANTE LE PROSSIME number SETTIMANE
        {$s = "\$week:" + $number.i + "\$"; }
    | DURANTE LE number SETTIMANE PROSSIME
        {$s = "\$week:" + $number.i + "\$"; }
    | DURANTE LE number PROSSIME SETTIMANE
        {$s = "\$week:" + $number.i + "\$"; }
    | NEL CORSO DELLA SETTIMANA PROSSIMA
        {$s = "\$week:1\$"; }
    | NEL CORSO DELLA PROSSIMA SETTIMANA
        {$s = "\$week:1\$"; }
    | NEL CORSO DI SETTIMANA PROSSIMA
        {$s = "\$week:1\$"; }
    | NEL CORSO DELLE PROSSIME number SETTIMANE
        {$s = "\$week:" + $number.i + "\$"; }
    | NEL CORSO DELLE number SETTIMANE PROSSIME
        {$s = "\$week:" + $number.i + "\$"; }
    | NEL CORSO DELLE number PROSSIME SETTIMANE
        {$s = "\$week:" + $number.i + "\$"; }
    | PER LA PROSSIMA SETTIMANA
        {$s = "\$week:1\$"; }
    | PER LA SETTIMANA PROSSIMA
        {$s = "\$week:1\$"; }
    | PER SETTIMANA PROSSIMA
        {$s = "\$week:1\$"; }
    | PER LE PROSSIME number SETTIMANE
        {$s = "\$week:" + $number.i + "\$"; }
    | PER LE number PROSSIME SETTIMANE
        {$s = "\$week:" + $number.i + "\$"; }
    | PER LE number SETTIMANE PROSSIME
        {$s = "\$week:" + $number.i + "\$"; }
    /* Past */
    | DURANTE LA SCORSA SETTIMANA
        {$s = "\$week:-1\$"; }
    | DURANTE LA SETTIMANA SCORSA
        {$s = "\$week:-1\$"; }
    | DURANTE SETTIMANA SCORSA
        {$s = "\$week:-1\$"; }
    | DURANTE LE SCORSE number SETTIMANE
        {$s = "\$week:-" + $number.i + "\$"; }
    | DURANTE LE number SETTIMANE SCORSE
        {$s = "\$week:-" + $number.i + "\$"; }
    | DURANTE LE number SCORSE SETTIMANE
        {$s = "\$week:-" + $number.i + "\$"; }
    | DURANTE LE number PASSATE SETTIMANE
        {$s = "\$week:-" + $number.i + "\$"; }
    | DURANTE LE number SETTIMANE PASSATE
        {$s = "\$week:-" + $number.i + "\$"; }
    | NEL CORSO DELLE SCORSE number SETTIMANE
        {$s = "\$week:-" + $number.i + "\$"; }
    | NEL CORSO DELLE number SETTIMANE SCORSE
        {$s = "\$week:-" + $number.i + "\$"; }
    | NEL CORSO DELLE number SCORSE SETTIMANE
        {$s = "\$week:-" + $number.i + "\$"; }
    | NEL CORSO DELLE number PASSATE SETTIMANE
        {$s = "\$week:-" + $number.i + "\$"; }
    | NEL CORSO DELLE number SETTIMANE PASSATE
        {$s = "\$week:-" + $number.i + "\$"; }
    ;

month_duration returns [String s]
    /* Future */
    : DURANTE IL PROSSIMO MESE
        {$s = "\$month:1\$"; }
    | DURANTE IL MESE PROSSIMO
        {$s = "\$month:1\$"; }
    | DURANTE I PROSSIMI number MESI
        {$s = "\$month:" + $number.i + "\$"; }
    | DURANTE I number MESI PROSSIMI
        {$s = "\$month:" + $number.i + "\$"; }
    | DURANTE I number PROSSIMI MESI
        {$s = "\$month:" + $number.i + "\$"; }
    | NEL CORSO DEL MESE PROSSIMO
        {$s = "\$month:1\$"; }
    | NEL CORSO DEL PROSSIMO MESE
        {$s = "\$month:1\$"; }
    | NEL CORSO DEI PROSSIMI number MESI
        {$s = "\$month:" + $number.i + "\$"; }
    | NEL CORSO DEI number MESI PROSSIMI
        {$s = "\$month:" + $number.i + "\$"; }
    | NEL CORSO DEI number PROSSIMI MESI
        {$s = "\$month:" + $number.i + "\$"; }
    | PER IL PROSSIMO MESE
        {$s = "\$month:1\$"; }
    | PER IL MESE PROSSIMO
        {$s = "\$month:1\$"; }
    | PER I PROSSIMI number MESI
        {$s = "\$month:" + $number.i + "\$"; }
    | PER I number PROSSIMI MESI
        {$s = "\$month:" + $number.i + "\$"; }
    | PER I number MESI PROSSIMI
        {$s = "\$month:" + $number.i + "\$"; }
    /* Past */
    | DURANTE LO SCORSO MESE
        {$s = "\$month:-1\$"; }
    | DURANTE IL MESE SCORSO
        {$s = "\$month:-1\$"; }
    | DURANTE GLI SCORSI number MESI
        {$s = "\$month:-" + $number.i + "\$"; }
    | DURANTE I number MESI SCORSI
        {$s = "\$month:-" + $number.i + "\$"; }
    | DURANTE I number SCORSI MESI
        {$s = "\$month:-" + $number.i + "\$"; }
    | DURANTE I number PASSATI MESI
        {$s = "\$month:-" + $number.i + "\$"; }
    | DURANTE I number MESI PASSATI
        {$s = "\$month:-" + $number.i + "\$"; }
    | NEL CORSO DEGLI SCORSI number MESI
        {$s = "\$month:-" + $number.i + "\$"; }
    | NEL CORSO DEI number MESI SCORSI
        {$s = "\$month:-" + $number.i + "\$"; }
    | NEL CORSO DEI number SCORSI MESI
        {$s = "\$month:-" + $number.i + "\$"; }
    | NEL CORSO DEI number PASSATI MESI
        {$s = "\$month:-" + $number.i + "\$"; }
    | NEL CORSO DEI number MESI PASSATI
        {$s = "\$month:-" + $number.i + "\$"; }
    ;

year_duration returns [String s]
    /* Future */
    : DURANTE IL PROSSIMO ANNO
        {$s = "\$year:1\$"; }
    | DURANTE L ANNO PROSSIMO
        {$s = "\$year:1\$"; }
    | DURANTE I PROSSIMI number ANNI
        {$s = "\$year:" + $number.i + "\$"; }
    | DURANTE I number ANNI PROSSIMI
        {$s = "\$year:" + $number.i + "\$"; }
    | DURANTE I number PROSSIMI ANNI
        {$s = "\$year:" + $number.i + "\$"; }
    | NEL CORSO DELL ANNO PROSSIMO
        {$s = "\$year:1\$"; }
    | NEL CORSO DEL PROSSIMO ANNO
        {$s = "\$year:1\$"; }
    | NEL CORSO DEI PROSSIMI number ANNI
        {$s = "\$year:" + $number.i + "\$"; }
    | NEL CORSO DEI number ANNI PROSSIMI
        {$s = "\$year:" + $number.i + "\$"; }
    | NEL CORSO DEI number PROSSIMI ANNI
        {$s = "\$year:" + $number.i + "\$"; }
    | PER IL PROSSIMO ANNO
        {$s = "\$year:1\$"; }
    | PER L ANNO PROSSIMO
        {$s = "\$year:1\$"; }
    | PER I PROSSIMI number ANNI
        {$s = "\$year:" + $number.i + "\$"; }
    | PER I number PROSSIMI ANNI
        {$s = "\$year:" + $number.i + "\$"; }
    | PER I number ANNI PROSSIMI
        {$s = "\$year:" + $number.i + "\$"; }
    /* Past */
    | DURANTE LO SCORSO ANNO
        {$s = "\$year:-1\$"; }
    | DURANTE L ANNO SCORSO
        {$s = "\$year:-1\$"; }
    | DURANTE GLI SCORSI number ANNI
        {$s = "\$year:-" + $number.i + "\$"; }
    | DURANTE I number ANNI SCORSI
        {$s = "\$year:-" + $number.i + "\$"; }
    | DURANTE I number SCORSI ANNI
        {$s = "\$year:-" + $number.i + "\$"; }
    | DURANTE I number PASSATI ANNI
        {$s = "\$year:-" + $number.i + "\$"; }
    | DURANTE I number ANNI PASSATI
        {$s = "\$year:-" + $number.i + "\$"; }
    | NEL CORSO DEGLI SCORSI number ANNI
        {$s = "\$year:-" + $number.i + "\$"; }
    | NEL CORSO DEI number ANNI SCORSI
        {$s = "\$year:-" + $number.i + "\$"; }
    | NEL CORSO DEI number SCORSI ANNI
        {$s = "\$year:-" + $number.i + "\$"; }
    | NEL CORSO DEI number PASSATI ANNI
        {$s = "\$year:-" + $number.i + "\$"; }
    | NEL CORSO DEI number ANNI PASSATI
        {$s = "\$year:-" + $number.i + "\$"; }
    ;

day_relative returns [String s]
    : OGGI
      {$s = "\$today\$"; }
    | DOMANI
      {$s = "\$tomorrow\$"; }
    | INDOMANI
      {$s = "\$tomorrow\$"; }
    | UN GIORNO DA ORA
      {$s = "\$tomorrow\$"; }
    | UN GIORNO DA ADESSO
      {$s = "\$tomorrow\$"; }
    | IERI
      {$s = "\$yesterday\$"; }
    | UN GIORNO FA
      {$s = "\$yesterday\$"; }
    | DOPO DOMANI
      {$s = "\$day_after_tomorrow\$"; }
    | DOPODOMANI
      {$s = "\$day_after_tomorrow\$"; }
    | ALTROIERI
      {$s = "\$day_before_yesterday\$"; }
    | IERLALTRO
      {$s = "\$day_before_yesterday\$"; }
    | number GIORNI DA ADESSO
          {$s = "\$day:" + $number.i + "\$"; }
    | number GIORNI DA ORA
          {$s = "\$day:" + $number.i + "\$"; }
    | number GIORNI DOPO
          {$s = "\$day:" + $number.i + "\$"; }
    | ENTRO number GIORNI
          {$s = "\$day:" + $number.i + "\$"; }
    | DOPO number GIORNI
          {$s = "\$day:" + $number.i + "\$"; }
    | FRA number GIORNI
          {$s = "\$day:" + $number.i + "\$"; }
    | number GIORNI FA
          {$s = "\$day:-" + $number.i + "\$"; }
    | number GIORNI PRIMA
          {$s = "\$day:-" + $number.i + "\$"; }
    | UN GIORNO PRIMA
          {$s = "\$day:-1\$"; }
    ;

day_absolute returns [String s]
    : LUNEDI
      {$s = "\$monday\$"; }
    | MARTEDI
      {$s = "\$tuesday\$"; }
    | MERCOLEDI
      {$s = "\$wednesday\$"; }
    | GIOVEDI
      {$s = "\$thursday\$"; }
    | VENERDI
      {$s = "\$friday\$"; }
    | SABATO
      {$s = "\$saturday\$"; }
    | DOMENICA
      {$s = "\$sunday\$"; }
    | WEEKEND
      {$s = "\$weekend\$"; }
    | WEEK END
      {$s = "\$weekend\$"; }
    | FINE SETTIMANA
      {$s = "\$weekend\$"; }
    ;

time_relative returns [String s]
    : ALBA
          {$s = "\$dawn\$"; }
    | MATTINO
          {$s = "\$morning\$"; }
    | MATTINA
          {$s = "\$morning\$"; }
    | DI MATTINA
          {$s = "\$morning\$"; }
    | IN MATTINATA
          {$s = "\$morning\$"; }
    | MEZZOGIORNO
          {$s = "\$noon\$"; }
    | A PRANZO
            {$s = "\$noon\$"; }
    | ALL ORA DI PRANZO
            {$s = "\$noon\$"; }
    | DOPO MEZZOGIORNO
          {$s = "\$afternoon\$"; }
    | POMERIGGIO
          {$s = "\$afternoon\$"; }
    | NEL POMERIGGIO
          {$s = "\$afternoon\$"; }
    | DOPO PRANZO
          {$s = "\$afternoon\$"; }
    | SERA
          {$s = "\$evening\$"; }
    | DI SERA
          {$s = "\$evening\$"; }
    | IN SERATA
          {$s = "\$evening\$"; }
    | A CENA
          {$s = "\$evening\$"; }
    | ALL ORA DI CENA
          {$s = "\$evening\$"; }
    | MEZZANOTTE
          {$s = "\$midnight\$"; }
    | NOTTE
          {$s = "\$night\$"; }
    | DI NOTTE
          {$s = "\$night\$"; }
    | IN NOTTATA
          {$s = "\$night\$"; }
    | ADESSO
          {$s = "\$now\$"; }
    | ORA
          {$s = "\$now\$"; }
    | QUESTO MOMENTO
            {$s = "\$now\$"; }
    | IN QUESTO MOMENTO
            {$s = "\$now\$"; }
    | AL MOMENTO
            {$s = "\$now\$"; }
    | PROPRIO ADESSO
            {$s = "\$now\$"; }
    | PROPRIO ORA
            {$s = "\$now\$"; }
    ;

month_relative returns [String s]
    : QUESTO MESE
          {$s = "\$month:0\$"; }
    | MESE SCORSO
          {$s = "\$month:-1\$"; }
    | SCORSO MESE
          {$s = "\$month:-1\$"; }
    | UN MESE FA
          {$s = "\$month:-1\$"; }
    | UN MESE PRIMA
          {$s = "\$month:-1\$"; }
    | MESE PROSSIMO
          {$s = "\$month:1\$"; }
    | PROSSIMO MESE
          {$s = "\$month:1\$"; }
    | MESE VENTURO
          {$s = "\$month:1\$"; }
    | FRA UN MESE
          {$s = "\$month:1\$"; }
    | DOPO UN MESE
          {$s = "\$month:1\$"; }
    | UN MESE DOPO
          {$s = "\$month:1\$"; }
    | FRA number MESI
          {$s = "\$month:" + $number.i + "\$"; }
    | DOPO number MESI
          {$s = "\$month:" + $number.i + "\$"; }
    | number MESI DOPO
          {$s = "\$month:" + $number.i + "\$"; }
    | number MESI FA
          {$s = "\$month:-" + $number.i + "\$"; }
    | number MESI PRIMA
          {$s = "\$month:-" + $number.i + "\$"; }
        ;

year_relative returns [String s]
    : QUEST ANNO
          {$s = "\$year:0\$"; }
    | ANNO SCORSO
          {$s = "\$year:-1\$"; }
    | SCORSO ANNO
          {$s = "\$year:-1\$"; }
    | UN ANNO FA
          {$s = "\$year:-1\$"; }
    | UN ANNO PRIMA
          {$s = "\$year:-1\$"; }
    | ANNO PROSSIMO
          {$s = "\$year:1\$"; }
    | ANNO VENTURO
          {$s = "\$year:1\$"; }
    | FRA UN ANNO
          {$s = "\$year:1\$"; }
    | DOPO UN ANNO
          {$s = "\$year:1\$"; }
    | UN ANNO DOPO
          {$s = "\$year:1\$"; }
    | FRA number ANNI
          {$s = "\$year:" + $number.i + "\$"; }
    | DOPO number ANNI
          {$s = "\$year:" + $number.i + "\$"; }
    | number ANNI DOPO
          {$s = "\$year:" + $number.i + "\$"; }
    | number ANNI FA
          {$s = "\$year:-" + $number.i + "\$"; }
    | number ANNI PRIMA
          {$s = "\$year:-" + $number.i + "\$"; }
    ;

week_number returns [int i]
    : PRIMA SETTIMANA
        {$i = 1; }
    | SECONDA SETTIMANA
        {$i = 2; }
    | TERZA SETTIMANA
        {$i = 3; }
    | QUARTA SETTIMANA
        {$i = 4; }
    | QUINTA SETTIMANA
        {$i = 5; }
    | SETTIMANA number
        {$i = $number.i; }
    ;

week_relative returns [String s]
    : QUESTA SETTIMANA
          {$s = "\$week:0\$"; }
    | IN SETTIMANA
        {$s = "\$week:0\$"; }
    | SETTIMANA SCORSA
          {$s = "\$week:-1\$"; }
    | SCORSA SETTIMANA
          {$s = "\$week:-1\$"; }
    | UNA SETTIMANA FA
          {$s = "\$week:-1\$"; }
    | UNA SETTIMANA PRIMA
          {$s = "\$week:-1\$"; }
    | SETTIMANA PROSSIMA
          {$s = "\$week:1\$"; }
    | SETTIMANA VENTURA
          {$s = "\$week:1\$"; }
    | PROSSIMA SETTIMANA
          {$s = "\$week:1\$"; }
    | FRA UNA SETTIMANA
          {$s = "\$week:1\$"; }
    | DOPO UNA SETTIMANA
          {$s = "\$week:1\$"; }
    | UNA SETTIMANA DOPO
          {$s = "\$week:1\$"; }
    | FRA number SETTIMANE
          {$s = "\$week:" + $number.i + "\$"; }
    | DOPO number SETTIMANE
          {$s = "\$week:" + $number.i + "\$"; }
    | ENTRO number SETTIMANE
          {$s = "\$week:" + $number.i + "\$"; }
    | number SETTIMANE DOPO
          {$s = "\$week:" + $number.i + "\$"; }
    | number SETTIMANE DA ADESSO
            {$s = "\$week:" + $number.i + "\$"; }
    | number SETTIMANE DA ORA
            {$s = "\$week:" + $number.i + "\$"; }
    | number SETTIMANE FA
          {$s = "\$week:-" + $number.i + "\$"; }
    | number SETTIMANE PRIMA
          {$s = "\$week:-" + $number.i + "\$"; }
    ;

year returns [String s]
    : YEARNUM
          {$s = $YEARNUM.text; }
    | NEL YEARNUM
          {$s = $YEARNUM.text; }
    | QUEST ANNO
          {$s = "\$year:0\$"; }
    | ANNO YEARNUM
          {$s = $YEARNUM.text; }
    | ANNO TIMENUM
          {$s = $TIMENUM.text; }
    | ANNO threedignum
          {$s = $threedignum.text; }
    | DOPO IL YEARNUM
            {$s = "\$afteryear:" + $YEARNUM.text + "\$" ; }
    | PRIMA DEL YEARNUM
              {$s = "\$beforeyear:" + $YEARNUM.text + "\$" ; }
    | DOPO L ANNO YEARNUM
              {$s = "\$afteryear:" + $YEARNUM.text + "\$" ; }
    | PRIMA DELL ANNO YEARNUM
              {$s = "\$beforeyear:" + $YEARNUM.text + "\$" ; }
    | ANNO SCORSO
          {$s = "\$year:-1\$"; }
    | SCORSO ANNO
          {$s = "\$year:-1\$"; }
    | ANNO PRECEDENTE
          {$s = "\$year:-1\$"; }
    | UN ANNO PRIMA
          {$s = "\$year:-1\$"; }
    | UN ANNO FA
          {$s = "\$year:-1\$"; }
    | ANNO PROSSIMO
          {$s = "\$year:1\$"; }
    | PROSSIMO ANNO
          {$s = "\$year:1\$"; }
    | ANNO VENTURO
          {$s = "\$year:1\$"; }
    | UN ANNO DA ADESSO
          {$s = "\$year:1\$"; }
    | UN ANNO DA ORA
          {$s = "\$year:1\$"; }
    | DOPO UN ANNO
          {$s = "\$year:1\$"; }
    | FRA UN ANNO
          {$s = "\$year:1\$"; }
    | DOPO IL YEARNUM
          {$s = "\$afteryear:" + $YEARNUM.text + "\$"; }
    | PRIMA DEL YEARNUM
          {$s = "\$beforeyear:" + $YEARNUM.text + "\$"; }
    | ANNI number
          {$s = "\$period:19" + $number.text + "\$"; }
    | number ANNI DA ADESSO
          {$s = "\$year:" + $number.i + "\$"; }
    | number ANNI DA ORA
          {$s = "\$year:" + $number.i + "\$"; }
    | number ANNI DOPO
          {$s = "\$year:" + $number.i + "\$"; }
    | DOPO number ANNI
          {$s = "\$year:" + $number.i + "\$"; }
    | FRA number ANNI
          {$s = "\$year:" + $number.i + "\$"; }
    | number ANNI FA
          {$s = "\$year:-" + $number.i + "\$"; }
    | number ANNI PRIMA
          {$s = "\$year:-" + $number.i + "\$"; }
    | ANNI YEARNUM
          {$s = "\$period:" + $YEARNUM.text + "\$"; }
    | ANNI TIMENUM
          {$s = "\$period:" + $TIMENUM.text + "\$"; }
    ;

date_repeat returns [String s]
    : OGNI GIORNO
          {$s = "\$daily\$"; }
    | QUOTIDIANAMENTE
          {$s = "\$daily\$"; }
    | TUTTI I GIORNI
          {$s = "\$daily\$"; }
    | GIORNALMENTE
          {$s = "\$daily\$"; }
    | GIORNO DOPO GIORNO
          {$s = "\$daily\$"; }
    | OGNI SETTIMANA
          {$s = "\$weekly\$"; }
    | SETTIMANALMENTE
          {$s = "\$weekly\$"; }
    | TUTTE LE SETTIMANE
          {$s = "\$weekly\$"; }
    | SETTIMANA DOPO SETTIMANA
          {$s = "\$weekly\$"; }
    | BISETTIMANALMENTE
          {$s = "\$biweekly\$"; }
    | OGNI DUE SETTIMANE
          {$s = "\$biweekly\$"; }
    | DUE VOLTE AL MESE
          {$s = "\$biweekly\$"; }
    | OGNI MESE
          {$s = "\$monthly\$"; }
    | MENSILMENTE
          {$s = "\$monthly\$"; }
    | TUTTI I MESI
          {$s = "\$monthly\$"; }
    | MESE DOPO MESE
          {$s = "\$monthly\$"; }
    | OGNI TRE MESI
          {$s = "\$quarterly\$"; }
    | TRIMESTRALMENTE
          {$s = "\$quarterly\$"; }
    | QUATTRO VOLTE ALL ANNO
          {$s = "\$quarterly\$"; }
    | QUATTRO VOLTE L ANNO
          {$s = "\$quarterly\$"; }
    | OGNI TRIMESTRE
          {$s = "\$quarterly\$"; }
    | OGNI ANNO
          {$s = "\$yearly\$"; }
    | TUTTI GLI ANNI
          {$s = "\$yearly\$"; }
    | ANNUALMENTE
          {$s = "\$yearly\$"; }
    ;

time_start returns [String s]
    : maybealle maybeore time_number
      {$s = $time_number.s; }
    ;

time_number returns [String s]
    : number INPUNTO
      {$s = String.format("%02d",$number.i) + ":_:_"; }
    /* 
    TODO this also takes dates if there are no slashes 
    */
    | a=number b=number
      {$s = "%02d" % ($a.i) + ":" + "%02d" % ($b.i) + ":_"; }
    | a=number ':' b=number
      {$s = "%02d" % ($a.i) + ":" + "%02d" % ($b.i) + ":_"; }

    | a=number E b=number
      {$s = "%02d" % ($a.i) + ":" + "%02d" % ($b.i) + ":_"; }
    | a=number MENO b=number
      {$s = "%02d" % (($b.i+23) % 24) + ":" + "%02d" % ((60-$a.i)) + ":_"; }
    | number E UN QUARTO
      {$s = "%02d" % ($number.i) + ":" + 15 + ":_"; }
    | UN QUARTO DOPO LE number
      {$s = "%02d" % ($number.i) + ":" + 15 + ":_"; }
    | number E TRE QUARTI
      {$s = "%02d" % ($number.i) + ":" + 45 + ":_"; }
    | UN QUARTO ALLE number
      {$s = "%02d" % (($number.i+23) % 24) + ":" + 45 + ":_"; }
    | number MENO UN QUARTO
      {$s = "%02d" % (($number.i+23) % 24) + ":" + 45 + ":_"; }
    | number E MEZZO
      {$s = "%02d" % ($number.i) + ":" + 30 + ":_"; }
    | threedignum
      {$s = "%02d" % (($threedignum.i / 100)) + ":" + "%02d" % (($threedignum.i % 100)) + ":_" ; }
    | ORE timenum
      {$s = "%02d" % (($timenum.i / 100)) + ":" + "%02d" % (($timenum.i % 100)) + ":_" ; }
    | timenum
      {$s = "%02d" % (($timenum.i / 100)) + ":" + "%02d" % (($timenum.i % 100)) + ":_" ; }
    | number
      {$s = String.format("%02d",$number.i) + ":_:_"; }
    ;

ampm returns [String s]
    : DEL MATTINO
      {$s = "\$am\$"; }
    | DI MATTINA
      {$s = "\$am\$"; }
    | DELLA NOTTE
      {$s = "\$am\$"; }
    | DI NOTTE
      {$s = "\$am\$"; }
    | DEL POMERIGGIO
      {$s = "\$pm\$"; }
    | DI POMERIGGIO
      {$s = "\$pm\$"; }
    | DELLA SERA
      {$s = "\$pm\$"; }
    | DI SERA
      {$s = "\$pm\$"; }
    ;

date returns [String s]
    // 16 novembre
    : number month
      {$s = "%02d" % ($month.i) + ":" + "%02d" % ($number.i); }
    // primo novembre
    | PRIMO month
    {$s = "%02d" % ($month.i) + ":01"; }
    // 16/11
  | a=number SLASH b=number
  {$s = "%02d" % ($b.i) + ":" + "%02d" % ($a.i); }
    // 16 di gennaio
  | number maybedi month
  {$s = "%02d" % ($month.i) + ":" + "%02d" % ($number.i); }
    // 16 di questo mese
    | number maybedi QUESTO MESE
      {$s = "_:" + "%02d" % ($number.i); }
    // novembre
  | month
  {$s = "%02d" % ($month.i) + ":_"; }
    ;

/*
    OPTIONAL RULES
*/
maybesettimana
    :
    | SETTIMANA
    ;

maybedi
    :
    | DI
    ;

maybethe
    :
    | IL
    ;
    
eand
    :
    | E
    ;
    
maybealle
    :
    | ALLE
    ;

maybeore
    :
    | ORE
    ;

month returns [int i]
    : GENNAIO
      {$i = 1; }
    | FEBBRAIO
      {$i = 2; }
    | MARZO
      {$i = 3; }
    | APRILE
      {$i = 4; }
    | MAGGIO
      {$i = 5; }
    | GIUGNO
      {$i = 6; }
    | LUGLIO
      {$i = 7; }
    | AGOSTO
      {$i = 8; }
    | SETTEMBRE
      {$i = 9; }
    | OTTOBRE
      {$i = 10; }
    | NOVEMBRE
      {$i = 11; }
    | DICEMBRE
      {$i = 12; }
    ;

duration returns [String s]
    : PER timecomponents
      {$s = $timecomponents.s; }
    | timecomponents
      {$s = $timecomponents.s; }
    ;

timecomponents returns [String s]
    : a=number ORE b=number MINUTI eand c=number SECONDI
      {$s = "%02d" % ($a.i) + ":" + "%02d" % ($b.i) + ":" + "%02d" % ($c.i) ; }
    | a=number ORE eand b=number MINUTI
      {$s = "%02d" % ($a.i) + ":" + "%02d" % ($b.i) + ":_"; }
    | a=number ORE eand b=number SECONDI
      {$s = "%02d" % ($a.i) + ":_:" + "%02d" % ($b.i) ; }
    | a=number MINUTI eand b=number SECONDI
      {$s = "_:" + "%02d" % ($a.i) + ":" + "%02d" % ($b.i) ; }
    | number ORE
          {$s = "%02d:_:_" % ($number.i) ; }
    | number ORE E UN QUARTO
          {$s = String.format("%02d:" + 15 + ":_", $number.i) ; }
    | number ORE E MEZZO
          {$s = String.format("%02d:" + 30 + ":_", $number.i) ; }
    | number ORE E TRE QUARTI
          {$s = String.format("%02d:" + 45 + ":_", $number.i) ; }
    | UN ORA E UN QUARTO
          {$s = "01:15:_" ; }
    | UN ORA E MEZZO
          {$s = "01:30:_" ; }
    | UN ORA E TRE QUARTI
          {$s = "01:45:_" ; }
    | UN ORA
          {$s = "01:_:_" ; }
    | number MINUTI
          {$s = "_:%02d:_" % ($number.i) ; }
    | number SECONDI
          {$s = "_:_:%02d" % ($number.i) ; }
    ;

rel_time_start returns [String s]
    : DOPO timecomponents
      {$s = "+:" + $timecomponents.s; }
    | FRA timecomponents
      {$s = "+:" + $timecomponents.s; }
    | timecomponents DOPO
      {$s = "+:" + $timecomponents.s; }
    | timecomponents DA ADESSO
      {$s = "+:" + $timecomponents.s; }
    | timecomponents DA ORA
      {$s = "+:" + $timecomponents.s; }
    | timecomponents FA
      {$s = "-:" + $timecomponents.s; }
    | timecomponents PRIMA
      {$s = "-:" + $timecomponents.s; }
    ;

season returns [String s]
    : AUTUNNO
        {$s = "\$autumn\$"; }
    | ESTATE
        {$s = "\$summer\$"; }
    | INVERNO
        {$s = "\$winter\$"; }
    | PRIMAVERA
        {$s = "\$spring\$"; }
    ;

holiday returns [String s]
    : FERRAGOSTO
        {$s = "\$feast_of_the_assumption\$"; }
    | NATALE
        {$s = "\$christmas\$"; }
    | PASQUA
        {$s = "\$easter\$"; }
    | SANVALENTINO
        {$s = "\$valentine\$"; }
    ;

season_relative returns [String s]
    : QUESTA STAGIONE
            {$s = "\$season:0\$"; }
    | STAGIONE SCORSA
            {$s = "\$season:-1\$"; }
    | SCORSA STAGIONE
            {$s = "\$season:-1\$"; }
    | UNA STAGIONE FA
            {$s = "\$season:-1\$"; }
    | UNA STAGIONE PRIMA
            {$s = "\$season:-1\$"; }
    | STAGIONE PROSSIMA
            {$s = "\$season:1\$"; }
    | PROSSIMA STAGIONE
            {$s = "\$season:1\$"; }
    | STAGIONE VENTURA
            {$s = "\$season:1\$"; }
    | FRA UNA STAGIONE
            {$s = "\$season:1\$"; }
    | DOPO UNA STAGIONE
            {$s = "\$season:1\$"; }
    | UNA STAGIONE DOPO
            {$s = "\$season:1\$"; }
    ;


/*
    NUMBER PARSING RULES
*/
number returns [int i]
    : NUMBER
      {$i = Integer.parseInt($NUMBER.text);}
    | UN
      {$i = 1 ;}
    | UNA
      {$i = 1 ;}
    | DUE
      {$i = 2 ;}
    | TRE
      {$i = 3 ;}
    | QUATTRO
      {$i = 4 ;}
    ;

threedignum returns [int i]
    : THREEDIGNUM
      {$i = Integer.parseInt($THREEDIGNUM.text);}
    ;

yearnum returns [int i]
    : YEARNUM
      {$i = Integer.parseInt($YEARNUM.text);}
    ;

timenum returns [int i]
    : TIMENUM
      {$i = Integer.parseInt($TIMENUM.text);}
    ;


/*
    LEXICON TERMINALS
    Parser rules are transformed into lexer rules
    Parser rules start with lowercase letters, lexer rules with uppercase
*/
A         : 'a' ;
ADESSO    : 'adesso' ;
AGOSTO    : 'ago''sto'? ;
AL        : 'al' ;
ALL       : 'all' ;
ALLE      : 'alle' ;
ALBA      : 'alba' ;
ANNI    : 'anni' ;
ANNO     : 'anno' ;
ANNUALMENTE     : 'annualmente' ;
APRILE     : 'apr''ile'? ;
AUTUNNO    : 'autunno' ;
BISETTIMANALMENTE : 'bisettimanalmente' ;
CENA       : 'cena' ;
CORSO      : 'corso' ;
DALLE      : 'dalle' ;
DA         : 'da' ;
DAL        : 'dal' ;
DEGLI      : 'degli' ;
DEI        : 'dei' ;
DEL        : 'del' ;
DELL      : 'dell' ;
DELLA     : 'della' ;
DELLE     : 'delle' ;
DI        : 'di' ;
DICEMBRE  : 'dic''embre'? ;
DOMANI    : 'domani' ;
DOMENICA  : 'dom''enica'? ;
DOMENICHE  : 'dom''eniche'? ;
DOPO     : 'dopo' ;
DOPODOMANI : 'dopodomani' ;
DUE      : 'due'|'2' ;
DURANTE  : 'durante' ;
E        : 'e' ;
END       : 'end' ;
ENTRO    : 'entro' ;
ESTATE   : 'estate' ;
FA      : 'fa' ;
FEBBRAIO   : 'feb''braio'? ;
FERRAGOSTO  : 'ferragosto' ;
FINE    : 'fine';
FRA      : [ft]'ra' ;
GENNAIO   : 'gen''n'?'naio'? ;
GIORNALMENTE  : 'giornalmente' ;
GIORNI     : 'giorni' ;
GIORNO      : 'giorno' ;
GIOVEDI     : 'gio''vedi'? ;
GIUGNO      : 'giu''gno'? ;
GLI       : 'gli' ;
IERI      : 'ieri' ;
I         : 'i' ;
IERLALTRO : 'ier''i'?' l altro';
IL        : 'il' ;
IN        : 'in' ;
INPUNTO   : 'in punto' ;
INVERNO   : 'inverno' ;
L         : 'l' ;
ALTROIERI : 'altro ieri' ;
INDOMANI : 'indomani' ;
LA        : 'la' ;
LE        : 'le' ;
LO        : 'lo' ;
LUGLIO   : 'lug''lio'? ;
LUNEDI     : 'lun''edi'? ;
MAGGIO       : 'mag''gio' ;
MARTEDI     : 'mar''tedi'? ;
MARZO      : 'marzo' ;
MATTINA     : 'mattina' ;
MATTINATA     : 'mattinata' ;
MATTINO     : 'mattino' ;
MENO     : 'meno' ;
MENSILMENTE : 'mensilmente' ;
MERCOLEDI  : 'mer''coledi'? ;
MESE      : 'mese' ;
MESI      : 'mesi' ;
MEZZANOTTE    : 'mezzanotte' ;
MEZZO      : 'mezz'[oa] ;
MEZZOGIORNO      : 'mezzogiorno' ;
MINUTI   : 'minuti' ;
MINUTO     : 'minuto' ;
MOMENTO    : 'momento' ;
NATALE     : 'natale' ;
NEL        : 'nel' ;
NOTTATA    : 'nottata' ;
NOTTE      : 'notte' ;
NOVEMBRE  : 'nov''embre'? ;
NUMBER    : [0-9][0-9]? ;
OGGI: 'oggi' ;
OGNI    : 'ogni' ;
ORA     : 'ora' ;
ORE     : 'ore' ;
OTTOBRE   : 'ott''obre'? ;
PASQUA    : 'pasqua' ;
PASSATE   : 'passate' ;
PASSATI   : 'passati' ;
PRANZO    : 'pranzo' ;
PRECEDENTE  : 'precedente' ;
PRECEDENTI  : 'precedenti' ;
PER        : 'per' ;
PIU        : 'piu' ;
POMERIGGIO : 'pomeriggio' ;
PRIMA      : 'prima' ;
PRIMAVERA  : 'primavera' ;
PRIMO      : 'primo' ;
PROPRIO    : 'proprio' ;
PROSSIMA   : 'prossima' ;
PROSSIME   : 'prossime' ;
PROSSIMI   : 'prossimi' ;
PROSSIMO   : 'prossimo' ;
QUARTA     : 'quarta' ;
QUARTI     : 'quarti' ;
QUARTO     : 'quarto' ;
QUATTRO    : 'quattro'|'4' ;
QUEST      : 'quest' ;
QUESTA     : 'questa' ;
QUESTO     : 'questo' ;
QUESTI     : 'questi' ;
QUINTA     : 'quinta' ;
QUINTO     : 'quinto' ;
QUOTIDIANAMENTE : 'quotidianamente' ;
SABATO    : 'sab''ato'? ;
SABATI    : 'sab''ati'? ;
SANVALENTINO : 'san valentino' ;
SCORSA    : 'scorsa' ;
SCORSE    : 'scorse' ;
SCORSI    : 'scorsi' ;
SCORSO    : 'scorso' ;
SECONDA  : 'seconda' ;
SECONDI  : 'secondi' ;
SECONDO  : 'secondo' ;
SERA      : 'sera' ;
SERATA    : 'serata' ;
SETTEMBRE : 'set''tembre'? ;
SETTIMANA   : 'settimana' ;
SETTIMANALMENTE : 'settimanalmente' ;
SETTIMANE  : 'settimane' ;
STAGIONE   : 'stagione' ;
STAGIONI   : 'stagionei' ;
STANOTTE   : 'stanotte' ;
STASERA    : 'stasera' ;
TARDI      : 'tardi' ;
TERZA     : 'terza' ;
TERZO     : 'terzo' ;
TRE       : 'tre'|'3' ;
TRIMESTRE : 'trimestre' ;
TRIMESTRALMENTE : 'trimestralmente' ;
TUTTE     : 'tutte' ;
TUTTI     : 'tutti' ;
ULTIMA    : 'ultima' ;
ULTIMI    : 'ultim'[ie] ;
ULTIMO    : 'ultimo' ;
UN        : 'un' ;
UNA       : 'una' ;
VENERDI  : 'ven''erdi'? ;
VENTURA   : 'ventura' ;
VENTURO   : 'venturo' ;
VOLTE     : 'volte' ;
WEEK      : 'week' ;
WEEKEND   : 'weekend' ;
WS        : [ \t\r\n]+ -> skip ;
SLASH     : '/' ;
THREEDIGNUM  : [0-9][0-9][0-9] ;
TIMENUM   : (([0][0-9])|([1][0-8])|([2][1-3]))[0-5][0-9] ;
YEARNUM   : ([0-9][0-9])[6-9][0-9]|([1][9]|[2][0])[0-5][0-9]|([2][4-9]|[3-9][0-9])[0-5][0-9] ;
YEAR19    : [2-9][0-9] ;
YEAR20    : [0-1][0-9] ;
