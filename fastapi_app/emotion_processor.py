"""
Emotion Analysis Processor Module
Handles emotion classification using rule-based approach with Indonesian lexicon
"""

import pandas as pd
import numpy as np
import re
from collections import Counter
from typing import Dict, List, Any


class EmotionProcessor:
    """Class untuk menangani emotion analysis dengan rule-based approach"""

    def __init__(self):
        """Initialize EmotionProcessor dengan emotion lexicons yang sangat komprehensif"""

        # Indonesian emotion lexicons - VERY COMPREHENSIVE
        self.emotion_lexicons = {
            'joy': [
                # Kebahagiaan umum
                'senang', 'gembira', 'bahagia', 'suka', 'riang', 'ceria', 'sumringah',
                'girang', 'sukacita', 'bergembira', 'bersuka', 'riang gembira',
                # Kepuasan
                'puas', 'memuaskan', 'terpuaskan', 'satisfying', 'satisfied', 'content',
                'lega', 'tenang', 'nyaman', 'aman', 'damai', 'tenteram',
                # Kualitas positif
                'mantap', 'mantul', 'mantab', 'josss', 'jos', 'joss', 'juara', 'super',
                'bagus', 'keren', 'hebat', 'top', 'terbaik', 'maksimal', 'optimal',
                'excellent', 'good', 'great', 'awesome', 'fantastic', 'wonderful',
                'amazing', 'outstanding', 'brilliant', 'superb', 'magnificent',
                # Kesuksesan
                'sukses', 'berhasil', 'success', 'successful', 'winning', 'win',
                'berjaya', 'menang', 'lancar', 'mulus', 'sempurna', 'perfect',
                # Kecepatan/efisiensi positif
                'cepat', 'kilat', 'instant', 'responsif', 'fast', 'quick', 'rapid',
                'efisien', 'smooth', 'lancar jaya',
                # Apresiasi
                'terima kasih', 'terimakasih', 'makasih', 'thanks', 'thank you',
                'appreciate', 'grateful', 'syukur', 'alhamdulillah', 'terima',
                # Rekomendasi positif
                'recommended', 'recommend', 'terpercaya', 'trusted', 'reliable',
                'worth it', 'worthed', 'oke banget', 'ok banget', 'cocok',
                # Keunggulan
                'unggul', 'superior', 'terdepan', 'nomor satu', 'no 1', 'number one',
                'profesional', 'berkualitas', 'kualitas', 'quality', 'premium',
                # Ekspresi senang
                'seneng', 'happy', 'happiness', 'cheerful', 'joyful', 'delighted',
                'seru', 'asik', 'asyik', 'menyenangkan', 'fun', 'enjoyable',
                # Cinta/suka
                'love', 'suka banget', 'cinta', 'favorit', 'favorite', 'fav',
                'terfavorit', 'kesukaan', 'idola',
                # Kagum
                'kagum', 'mengagumkan', 'impressive', 'impressed', 'inspiring',
                'memukau', 'menakjubkan', 'spektakuler', 'spectacular',
                # Stabilitas positif
                'stabil', 'stable', 'konsisten', 'consistent', 'terjamin',
                'solid', 'kuat', 'tangguh', 'handal'
            ],
            'anger': [
                # Kemarahan dasar
                'marah', 'angry', 'anger', 'rage', 'furious', 'mad',
                'murka', 'geram', 'mengamuk', 'berang', 'gusar',
                # Kekesalan
                'kesal', 'jengkel', 'dongkol', 'sebal', 'sebel', 'annoyed',
                'annoying', 'menyebalkan', 'menjengkelkan', 'irritated', 'upset',
                'gondok', 'gemes', 'geregetan', 'bete', 'bt',
                # Kebencian
                'benci', 'hate', 'hatred', 'muak', 'jijay', 'antipati',
                'tidak suka', 'ga suka', 'gak suka', 'nggak suka',
                # Kata kasar
                'bangsat', 'sialan', 'kampret', 'brengsek', 'keparat', 'bajingan',
                'fuck', 'shit', 'damn', 'hell', 'asshole', 'bitch',
                'anjing', 'anjir', 'anjay', 'anjrit', 'anj', 'ajg', 'anjg',
                'goblok', 'tolol', 'bodoh', 'idiot', 'stupid', 'dungu', 'bego',
                'tai', 'kontol', 'memek', 'pepek', 'jancuk', 'jancok',
                # Ketidakprofesionalan
                'tidak profesional', 'ga profesional', 'gak profesional',
                'kurang profesional', 'unprofessional', 'amatir', 'amateur',
                'asal', 'sembarangan', 'acak', 'ngaco', 'kacau', 'chaos',
                # Kualitas buruk
                'payah', 'parah', 'teruk', 'jelek banget', 'buruk sekali',
                'worst', 'terrible', 'horrible', 'awful', 'disgusting',
                'menyebalkan', 'mengecewakan', 'disappointing',
                # Keluhan keras
                'protes', 'complain', 'komplain', 'keluhkan', 'report',
                'laporkan', 'somasi', 'tuntut', 'gugat',
                # Ancaman/peringatan
                'boikot', 'boycott', 'blacklist', 'batalkan', 'cancel',
                'unsubscribe', 'berhenti', 'stop', 'jangan lagi', 'kapok',
                # Ketidakadilan
                'curang', 'tipu', 'bohong', 'penipuan', 'scam', 'fraud',
                'nipu', 'menipu', 'penipu', 'pembohong', 'liar', 'hoax'
            ],
            'sadness': [
                # Kesedihan dasar
                'sedih', 'sad', 'sadness', 'sorrow', 'grief', 'unhappy',
                'duka', 'pilu', 'nelangsa', 'sendu', 'murung', 'gloomy',
                # Kekecewaan
                'kecewa', 'disappointed', 'disappointing', 'mengecewakan',
                'zonk', 'gagal', 'failure', 'failed', 'fail',
                'hancur', 'broken', 'terpuruk', 'jatuh', 'down',
                # Depresi
                'depresi', 'depressed', 'depression', 'hopeless', 'putus asa',
                'frustasi', 'frustrated', 'frustrasi', 'stress', 'tertekan',
                # Kegelisahan sedih
                'galau', 'bingung', 'confused', 'lost', 'tersesat',
                'ragu', 'doubt', 'uncertain', 'tidak yakin',
                # Penyesalan
                'menyesal', 'regret', 'rugi', 'loss', 'sia sia', 'percuma',
                'sayang', 'kasihan', 'pity', 'pathetic', 'menyedihkan',
                # Kelelahan emosional
                'capek', 'lelah', 'tired', 'exhausted', 'burnout',
                'jenuh', 'bosan', 'bored', 'boring', 'membosankan',
                'penat', 'letih', 'lemas', 'lemah', 'weak',
                # Kehilangan harapan
                'menyerah', 'give up', 'resign', 'pasrah', 'tamat',
                'berakhir', 'end', 'ending', 'selesai sudah', 'habis',
                # Kerinduan/kehilangan
                'rindu', 'miss', 'missing', 'hilang', 'kehilangan', 'lost',
                'pergi', 'gone', 'ditinggal', 'abandoned',
                # Penderitaan
                'menderita', 'suffering', 'sakit', 'pain', 'painful',
                'tersiksa', 'torture', 'sengsara', 'misery', 'miserable',
                # Tragis
                'tragis', 'tragic', 'tragedy', 'tragedi', 'naas', 'malang',
                'sial', 'unlucky', 'nasib buruk'
            ],
            'fear': [
                # Ketakutan dasar
                'takut', 'fear', 'scared', 'afraid', 'frightened', 'terrified',
                'ngeri', 'seram', 'menakutkan', 'scary', 'spooky', 'creepy',
                # Kekhawatiran
                'khawatir', 'worried', 'worry', 'concern', 'concerned',
                'cemas', 'anxious', 'anxiety', 'gelisah', 'resah', 'risau',
                'was was', 'was-was', 'waswas', 'hawatir',
                # Panik
                'panik', 'panic', 'kalut', 'kacau', 'bingung panik',
                'deg degan', 'deg-degan', 'tegang', 'tense', 'nervous',
                'grogi', 'gugup', 'gemetar', 'trembling',
                # Bahaya
                'bahaya', 'dangerous', 'danger', 'berbahaya', 'unsafe',
                'berisiko', 'risky', 'risk', 'rawan', 'rawan bahaya',
                'ancaman', 'threat', 'mengancam', 'threatening',
                # Ketidakamanan
                'tidak aman', 'ga aman', 'gak aman', 'insecure',
                'rawan', 'rentan', 'vulnerable', 'lemah',
                # Horor
                'horor', 'horror', 'menyeramkan', 'mengerikan', 'horrifying',
                'menakutkan', 'frightening', 'terrifying',
                # Ketakutan spesifik
                'trauma', 'traumatic', 'fobia', 'phobia', 'nightmare',
                'mimpi buruk', 'ketakutan', 'paranoid', 'paranoia',
                # Keraguan takut
                'ragu takut', 'takut takut', 'was was', 'jangan jangan',
                'mudah mudahan tidak', 'semoga tidak', 'hopefully not',
                # Shock takut
                'shock', 'shocked', 'kaget takut', 'terkejut takut',
                'oh no', 'oh tidak', 'aduh', 'ampun', 'tolong',
                # Antisipasi negatif
                'jangan sampai', 'mudah mudahan aman', 'hati hati',
                'waspada', 'alert', 'awas', 'careful', 'be careful'
            ],
            'surprise': [
                # Kejutan dasar
                'kaget', 'terkejut', 'surprised', 'surprise', 'shocking',
                'shocked', 'shock', 'mengejutkan', 'mencengangkan',
                # Heran
                'heran', 'terheran', 'wonder', 'wondering', 'curious',
                'penasaran', 'aneh', 'strange', 'weird', 'odd',
                # Takjub
                'takjub', 'amazed', 'amazing', 'awe', 'awesome',
                'menakjubkan', 'memukau', 'impressive', 'spectacular',
                # Tidak percaya
                'tidak percaya', 'ga percaya', 'gak percaya', 'unbelievable',
                'incredible', 'serius', 'serious', 'beneran', 'really',
                'masa', 'masa sih', 'apa iya', 'benarkah', 'is it true',
                # Ekspektasi meleset
                'unexpected', 'tiba tiba', 'tiba-tiba', 'mendadak',
                'terduga', 'tidak terduga', 'diluar dugaan',
                'ternyata', 'rupanya', 'oh ternyata', 'oh rupanya',
                # Ekspresi kaget
                'wow', 'woah', 'waw', 'wih', 'wiw', 'wah', 'weh',
                'gila', 'gile', 'gokil', 'gilak', 'gilaaa',
                'anjir', 'anjay', 'anjrit', 'astaga', 'astagfirullah',
                'masyaallah', 'subhanallah', 'ya allah', 'ya ampun',
                # Pertanyaan kaget
                'serius', 'serius nih', 'beneran', 'kok bisa', 'gimana bisa',
                'how come', 'what', 'apa', 'hah', 'lho', 'loh', 'lo',
                'eh', 'eeh', 'heh', 'ha', 'what the',
                # Reaksi spontan
                'omg', 'oh my god', 'oh my', 'god', 'demi apa',
                'demi tuhan', 'ampun dah', 'asli', 'bener bener',
                # Plot twist
                'plot twist', 'twist', 'balik', 'kebalikan',
                'berlawanan', 'kontras', 'berbeda', 'beda banget'
            ],
            'disgust': [
                # Jijik dasar
                'jijik', 'jijay', 'disgusting', 'disgust', 'gross',
                'ew', 'eww', 'yuck', 'yikes', 'ugh',
                # Mual
                'muak', 'mual', 'enek', 'eneg', 'muntah', 'nauseous',
                'pengen muntah', 'mau muntah', 'bikin mual', 'bikin muntah',
                # Jijik fisik
                'jorok', 'kotor', 'dirty', 'filthy', 'najis', 'cemar',
                'busuk', 'bau', 'smelly', 'stink', 'basi', 'rotten',
                # Jijik moral
                'menjijikkan', 'hina', 'rendah', 'low', 'despicable',
                'memalukan', 'shameful', 'shame', 'embarrassing',
                # Kualitas sangat buruk
                'buruk', 'jelek', 'ugly', 'bad', 'terrible', 'awful',
                'horrible', 'worst', 'terburuk', 'paling jelek',
                'sampah', 'trash', 'garbage', 'rubbish', 'waste',
                # Horor/seram (disgust variant)
                'menyeramkan', 'mengerikan', 'horrifying', 'horrific',
                'menakutkan', 'disturbing', 'disturb', 'mengganggu',
                # Tidak manusiawi
                'keji', 'kejam', 'cruel', 'sadis', 'sadistic',
                'biadab', 'brutal', 'kasar', 'harsh', 'rough',
                # Penolakan keras
                'tolak', 'reject', 'menolak', 'tidak mau', 'ga mau',
                'ogah', 'males', 'kapok', 'jangan', 'no way',
                # Kualitas rendah ekstrem
                'parah', 'parah banget', 'teruk', 'buruk sekali',
                'ancur', 'hancur', 'destroyed', 'rusak parah',
                # Kata kasar disgust
                'tai', 'taik', 'shit', 'crap', 'poop',
                'babi', 'pig', 'swine', 'bangkai', 'sampah masyarakat'
            ]
        }

    def preprocess_text(self, text: str) -> str:
        """
        Preprocessing text untuk emotion analysis

        Args:
            text: Raw text input

        Returns:
            Cleaned text
        """
        if pd.isna(text) or text == '':
            return ""

        text = str(text)

        # COMPREHENSIVE Emoji dictionary - mapping ke emotion keywords
        emoji_dict = {
            # JOY emotions - kebahagiaan, kegembiraan, kepuasan
            '😀': 'senang gembira', '😃': 'senang riang', '😄': 'senang ceria',
            '😁': 'senang senyum', '😆': 'tertawa senang', '😅': 'senang lega',
            '🤣': 'tertawa bahagia', '😂': 'lucu senang', '🙂': 'senang',
            '🙃': 'senang', '��': 'senang', '😊': 'senang puas',
            '😇': 'senang baik', '🥰': 'suka cinta', '😍': 'suka cinta',
            '🤩': 'kagum senang', '😘': 'suka sayang', '😗': 'suka',
            '☺️': 'senang', '😚': 'suka', '😙': 'suka',
            '🥲': 'senang terharu', '😋': 'senang nikmat', '😛': 'senang',
            '😜': 'senang seru', '🤪': 'senang gokil', '😝': 'senang',
            '🤑': 'senang untung', '🤗': 'senang hangat', '🤭': 'senang malu',
            '🫢': 'kaget senang', '🫣': 'senang malu', '🤫': 'senang',
            '🤔': 'heran', '🫡': 'bagus', '🤐': 'diam',
            # Heart & love symbols
            '❤️': 'suka cinta love', '🧡': 'suka cinta', '💛': 'suka cinta',
            '💚': 'suka cinta', '💙': 'suka cinta', '💜': 'suka cinta',
            '🖤': 'suka', '🤍': 'suka cinta', '🤎': 'suka',
            '💕': 'suka cinta', '💞': 'suka cinta', '💓': 'suka cinta',
            '💗': 'suka cinta', '💖': 'suka cinta', '💘': 'suka cinta',
            '💝': 'suka cinta', '💟': 'suka cinta', '❣️': 'suka cinta',
            '❤️‍🔥': 'suka cinta mantap', '❤️‍🩹': 'sedih kecewa',
            # Positive gestures
            '👍': 'bagus setuju oke', '👏': 'bagus hebat', '🙌': 'bagus senang',
            '👌': 'oke bagus', '🤌': 'bagus', '🤏': 'sedikit',
            '✌️': 'bagus damai', '🤞': 'berharap', '🫰': 'bagus',
            '🤟': 'suka love', '🤘': 'keren', '🤙': 'oke',
            '👈': 'ini', '👉': 'itu', '👆': 'atas',
            '🫵': 'kamu', '👇': 'bawah', '☝️': 'penting',
            '👊': 'semangat', '✊': 'semangat', '🤛': 'semangat',
            '🤜': 'semangat', '🫶': 'cinta suka', '🙏': 'terima kasih mohon',
            # Fire & celebration
            '🔥': 'mantap bagus keren', '💯': 'bagus sempurna maksimal',
            '⭐': 'bagus bintang', '🌟': 'bagus cemerlang', '✨': 'bagus cemerlang',
            '💫': 'bagus', '⚡': 'cepat mantap', '💥': 'mantap dahsyat',
            '🎉': 'senang perayaan', '🎊': 'senang perayaan', '🎈': 'senang',
            '🎁': 'senang hadiah', '🎀': 'senang', '🎆': 'senang perayaan',
            '🎇': 'senang perayaan', '🧨': 'perayaan',
            # Trophy & success
            '🏆': 'juara sukses menang', '🥇': 'juara terbaik', '🥈': 'bagus',
            '🥉': 'bagus', '🏅': 'juara bagus', '🎖️': 'bagus',

            # ANGER emotions - kemarahan, kekesalan
            '😠': 'marah kesal', '😡': 'marah geram', '🤬': 'marah bangsat',
            '😤': 'kesal dongkol', '😾': 'marah kesal', '👿': 'marah jahat',
            '😈': 'jahat', '💢': 'marah kesal', '💥': 'marah meledak',
            '🔪': 'bahaya marah', '🗡️': 'bahaya marah', '⚔️': 'perang marah',
            '💣': 'marah meledak', '🧨': 'marah meledak',
            # Negative gestures
            '👎': 'jelek buruk tidak setuju', '🖕': 'marah bangsat',
            '✋': 'stop berhenti', '🛑': 'stop berhenti', '⛔': 'tidak boleh',
            '🚫': 'tidak boleh dilarang', '❌': 'salah tidak boleh',
            '❎': 'salah tidak', '⭕': 'salah', '🚷': 'dilarang',
            '🚯': 'dilarang', '🚳': 'dilarang', '🚱': 'dilarang',
            '📵': 'dilarang', '🔞': 'dilarang', '☢️': 'bahaya',
            '☣️': 'bahaya', '⚠️': 'bahaya hati hati',

            # SADNESS emotions - kesedihan, kekecewaan
            '😢': 'sedih menangis', '😭': 'sedih menangis kecewa', '😿': 'sedih menangis',
            '😥': 'sedih kecewa', '😰': 'sedih cemas', '😓': 'sedih capek',
            '😞': 'sedih kecewa', '😔': 'sedih murung', '😟': 'sedih khawatir',
            '😕': 'sedih bingung', '🙁': 'sedih', '☹️': 'sedih',
            '😣': 'sedih frustasi', '😖': 'sedih tersiksa', '😫': 'sedih lelah',
            '😩': 'sedih frustasi', '🥺': 'sedih kasihan mohon', '😪': 'sedih lelah',
            '🤤': 'sedih', '😴': 'bosan lelah', '😵': 'pusing bingung',
            '😵‍💫': 'pusing bingung', '🫤': 'kecewa', '🥱': 'bosan',
            '😮‍💨': 'lelah lega', '😶‍🌫️': 'bingung',
            # Broken & negative
            '💔': 'sedih kecewa patah hati', '🖤': 'sedih gelap', '⚫': 'sedih gelap',
            '💀': 'mati hancur', '☠️': 'mati hancur', '👻': 'takut',

            # FEAR emotions - ketakutan, kekhawatiran
            '😨': 'takut cemas', '😱': 'takut shock', '😰': 'takut khawatir',
            '😧': 'takut cemas', '😦': 'takut kaget', '😮': 'kaget takut',
            '😯': 'kaget heran', '😲': 'kaget shock', '🫨': 'takut gemetar',
            '😳': 'kaget malu', '🥶': 'takut dingin', '🫣': 'takut malu',
            '😬': 'takut canggung', '🫢': 'kaget takut', '🤐': 'takut diam',
            '🙊': 'takut', '🙈': 'takut malu', '🙉': 'takut',
            # Scary & dangerous
            '👹': 'takut seram', '👺': 'takut marah', '💀': 'takut mati',
            '☠️': 'bahaya takut', '👻': 'takut hantu', '👽': 'takut aneh',
            '👾': 'takut', '🤖': 'robot', '😈': 'jahat takut',
            '👿': 'jahat marah takut', '🔥': 'bahaya',

            # SURPRISE emotions - kejutan, heran
            '😮': 'kaget heran', '😯': 'kaget heran', '😲': 'kaget shock wow',
            '🤯': 'kaget gila shock', '😳': 'kaget malu heran', '🫢': 'kaget',
            '🫣': 'kaget', '🤭': 'kaget', '😱': 'kaget shock takut',
            '🙀': 'kaget shock', '😧': 'kaget cemas', '😦': 'kaget',
            '🫨': 'kaget gemetar', '🤔': 'heran bingung', '🧐': 'heran',
            '🫥': 'heran hilang', '😶': 'heran diam', '🫡': 'wow',
            # Explosive & surprising
            '💥': 'wow dahsyat', '💫': 'wow', '✨': 'wow cemerlang',
            '🌟': 'wow bintang', '⭐': 'wow', '🌠': 'wow',
            '🎆': 'wow', '🎇': 'wow', '🧨': 'wow',
            '🤯': 'gila wow shock', '🎉': 'wow perayaan', '🎊': 'wow perayaan',

            # DISGUST emotions - jijik, muak
            '🤢': 'mual jijik', '🤮': 'muntah jijik mual', '🤧': 'sakit',
            '😷': 'sakit', '🤒': 'sakit', '🤕': 'sakit',
            '🥴': 'mual pusing', '😵': 'pusing', '🫠': 'hancur',
            '🤑': 'serakah', '🥵': 'panas', '🥶': 'dingin',
            # Poop & dirty
            '💩': 'tai jelek jijik', '🚽': 'toilet', '🧻': 'kotor',
            '🗑️': 'sampah jelek', '♻️': 'daur ulang', '⚰️': 'mati',
            '🪦': 'mati', '🩸': 'darah', '🦠': 'virus jijik',
            # Negative animals
            '🐀': 'tikus jijik', '🐁': 'tikus', '🕷️': 'laba jijik',
            '🦂': 'kalajengking bahaya', '🐍': 'ular bahaya',

            # NEUTRAL with slight emotion hints
            '😐': 'datar', '😑': 'datar bosan', '😶': 'diam',
            '🫥': 'hilang', '🙄': 'bosan', '😏': 'sinis',
            '😒': 'bosan malas', '🤨': 'curiga heran', '🧐': 'heran',
            '🤓': 'pintar', '😎': 'keren', '🥸': 'menyamar',
            '🤡': 'badut lucu', '🥳': 'senang perayaan', '🥴': 'mabuk pusing',
            '😌': 'tenang', '😔': 'sedih', '😪': 'ngantuk bosan',

            # Additional symbols
            '✅': 'benar bagus setuju', '☑️': 'benar setuju', '✔️': 'benar bagus',
            '💚': 'oke bagus', '🆗': 'oke', '🆒': 'keren',
            '🆕': 'baru', '🆓': 'gratis', '🎯': 'tepat bagus',
            '📈': 'naik bagus', '📉': 'turun jelek', '💹': 'untung',
            '💸': 'mahal rugi', '💰': 'uang untung', '💵': 'uang',
            '💴': 'uang', '💶': 'uang', '💷': 'uang',
            '🤑': 'untung serakah', '🏧': 'atm uang',
            # Communication
            '📱': 'hp telepon', '📲': 'telepon', '☎️': 'telepon',
            '📞': 'telepon', '📟': 'pager', '📠': 'fax',
            '💻': 'komputer laptop', '🖥️': 'komputer', '⌨️': 'keyboard',
            '🖱️': 'mouse', '🖨️': 'printer', '💾': 'save',
            '💿': 'cd', '📀': 'dvd', '🧮': 'hitung',
            # Internet & network
            '📶': 'sinyal internet', '📡': 'sinyal antena', '🛜': 'wifi',
            '📳': 'getar', '📴': 'mati', '🔋': 'baterai',
            '🪫': 'lowbat', '🔌': 'charger', '💡': 'ide bagus',
            '🔦': 'lampu', '🕯️': 'lilin', '🪔': 'lampu',
            # Speed & time
            '⚡': 'cepat kilat', '💨': 'cepat', '🏃': 'lari cepat',
            '🏃‍♀️': 'lari cepat', '🏃‍♂️': 'lari cepat',
            '⏰': 'waktu', '⏱️': 'waktu', '⏲️': 'waktu',
            '⌚': 'jam', '⌛': 'waktu habis', '⏳': 'waktu',
            '🕐': 'jam', '🕑': 'jam', '🕒': 'jam',
            # Weather (emotion triggers)
            '☀️': 'cerah bagus', '🌤️': 'bagus', '⛅': 'oke',
            '🌥️': 'mendung', '☁️': 'mendung', '🌦️': 'hujan',
            '🌧️': 'hujan sedih', '⛈️': 'badai', '🌩️': 'petir bahaya',
            '⚡': 'petir cepat', '❄️': 'dingin', '🌨️': 'salju',
            '☃️': 'salju', '⛄': 'salju', '🌬️': 'angin',
            '💧': 'air', '💦': 'basah', '☔': 'hujan',
            '🌊': 'ombak', '🌈': 'bagus indah'
        }

        # Convert emoji to text
        for emoji, replacement in emoji_dict.items():
            text = text.replace(emoji, f' {replacement} ')

        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)

        # Remove mentions
        text = re.sub(r'@\w+', '', text)

        # Process hashtags
        def process_hashtag(match):
            hashtag = match.group(1)
            camel_split = re.sub('([a-z])([A-Z])', r'\1 \2', hashtag)
            return camel_split.lower()

        text = re.sub(r'#(\w+)', process_hashtag, text)

        # Remove remaining emojis
        emoji_pattern = re.compile("["
                                  u"\U0001F600-\U0001F64F"
                                  u"\U0001F300-\U0001F5FF"
                                  u"\U0001F680-\U0001F6FF"
                                  u"\U0001F1E0-\U0001F1FF"
                                  u"\U00002702-\U000027B0"
                                  u"\U000024C2-\U0001F251"
                                  "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r' ', text)

        # Lowercase
        text = text.lower()

        # Normalize repeated characters
        text = re.sub(r'(.)\1{3,}', r'\1\1', text)

        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def predict_emotion(self, text: str) -> str:
        """
        Predict emotion menggunakan rule-based lexicon matching

        Args:
            text: Cleaned text

        Returns:
            Emotion label: 'joy', 'anger', 'sadness', 'fear', 'surprise', 'disgust'
        """
        if not text or len(text.strip()) == 0:
            return 'neutral'

        text_lower = text.lower()
        emotion_scores = {emotion: 0 for emotion in self.emotion_lexicons.keys()}

        # Count emotion words
        for emotion, words in self.emotion_lexicons.items():
            for word in words:
                if word in text_lower:
                    # Give higher weight to exact word matches
                    if f' {word} ' in f' {text_lower} ':
                        emotion_scores[emotion] += 2
                    else:
                        emotion_scores[emotion] += 1

        # Get dominant emotion
        max_score = max(emotion_scores.values())

        if max_score == 0:
            return 'neutral'

        # Return emotion with highest score
        for emotion, score in emotion_scores.items():
            if score == max_score:
                return emotion

        return 'neutral'

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'full_text') -> pd.DataFrame:
        """
        Analyze emotion untuk seluruh DataFrame

        Args:
            df: DataFrame dengan kolom text
            text_column: Nama kolom yang berisi text

        Returns:
            DataFrame dengan kolom tambahan 'cleaned_text' dan 'emotion'
        """
        # Preprocessing
        df['cleaned_text'] = df[text_column].apply(self.preprocess_text)

        # Remove empty texts
        df = df[df['cleaned_text'].str.len() > 0].copy()

        # Predict emotions
        df['emotion'] = df['cleaned_text'].apply(self.predict_emotion)

        print(f"✓ Emotion prediction completed on {len(df)} texts")

        return df

    def get_word_frequency(self, texts: pd.Series, n: int = 50) -> List[Dict[str, Any]]:
        """
        Get top N words dari texts

        Args:
            texts: Series of texts
            n: Number of top words to return

        Returns:
            List of dicts with 'text' and 'value' keys
        """
        all_words = ' '.join(texts).split()
        # Filter kata yang lebih dari 2 karakter
        all_words = [word for word in all_words if len(word) > 2]
        word_freq = Counter(all_words).most_common(n)
        return [{'text': word, 'value': count} for word, count in word_freq]

    def generate_emotion_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive emotion analysis report

        Args:
            df: DataFrame dengan kolom 'emotion', 'cleaned_text', 'favorite_count',
                'retweet_count', 'conversation_id_str'

        Returns:
            Dictionary dengan emotion distribution, engagement stats, dan wordcloud data
        """
        total = len(df)

        # 1. Emotion Distribution
        emotion_counts = df['emotion'].value_counts().to_dict()
        emotion_distribution = {
            emotion: {
                'count': int(count),
                'percentage': round((count / total) * 100, 2)
            }
            for emotion, count in emotion_counts.items()
        }

        # 2. Calculate Engagement per emotion
        # Engagement = Likes + Retweets + Replies count
        df['engagement'] = 0

        # Add likes (favorite_count)
        if 'favorite_count' in df.columns:
            df['engagement'] += df['favorite_count'].fillna(0)

        # Add retweets (retweet_count)
        if 'retweet_count' in df.columns:
            df['engagement'] += df['retweet_count'].fillna(0)

        # Add count of replies per conversation
        if 'conversation_id_str' in df.columns:
            reply_counts = df.groupby('conversation_id_str').size()
            df['conversation_reply_count'] = df['conversation_id_str'].map(reply_counts)
            df['engagement'] += df['conversation_reply_count'].fillna(0)

        # Sum engagement by emotion
        emotion_by_engagement = df.groupby('emotion')['engagement'].sum().to_dict()
        emotion_by_engagement = {k: int(v) for k, v in emotion_by_engagement.items()}

        # 3. Word frequency untuk word cloud per emotion
        wordcloud_data = {}
        emotions = ['joy', 'anger', 'sadness', 'fear', 'surprise', 'disgust', 'neutral']

        for emotion in emotions:
            emotion_texts = df[df['emotion'] == emotion]['cleaned_text']
            if len(emotion_texts) > 0:
                wordcloud_data[emotion] = self.get_word_frequency(emotion_texts, n=50)
            else:
                wordcloud_data[emotion] = []

        report = {
            'emotion_distribution': emotion_distribution,
            'emotion_by_engagement': emotion_by_engagement,
            'wordcloud_data': wordcloud_data,
            'total_analyzed': total,
            'metadata': {
                'data_source': 'processed_dataframe',
                'emotion_method': 'rule_based_lexicon',
                'emotions': ['joy', 'anger', 'sadness', 'fear', 'surprise', 'disgust', 'neutral'],
                'engagement_calculation': 'likes (favorite_count) + retweets (retweet_count) + replies (conversation_reply_count)'
            }
        }

        return report
