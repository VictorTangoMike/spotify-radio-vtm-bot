import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import json
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET') 
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
PLAYLIST_ID = '4Jkif9JOC1pvOesEnejcO2'
WELCOME_ALBUM_ID = '56DxAA2hEm2S8Lsh1ih9Qq'
USERNAME = os.getenv('SPOTIFY_USERNAME')

PODCAST_1_ID = '4Z5CoK9UJq3ykgLbcBTQwP'
PODCAST_2_ID = '1jFei5HTzmuPNPJVzlnjQC'
INTELIGENCIA_LTDA_ID = '14jalMOh1Jr77eTRUdN6X9'

PODCASTS_ROTATIVOS = [
    '4DVtjWhxeIUge0LRku74ih',
    '14jalMOh1Jr77eTRUdN6X9',
    '71mG5GljNdYLXLzjWY9Apm',
    '59fUC0CFgoMfiLDXCuhjUM',
    '22Wgt4ASeaw8mmoqAWNUn1',
    '0qfFcilKpNKkXy8TbZ4moP',
]

NOMES_PODCASTS = {
    '4Z5CoK9UJq3ykgLbcBTQwP': 'Flow News (Slot 1)',
    '1jFei5HTzmuPNPJVzlnjQC': 'News Podcast 2',
    '14jalMOh1Jr77eTRUdN6X9': 'Inteligência LTDA',
    '4DVtjWhxeIUge0LRku74ih': 'Farol de Pouso',
    '71mG5GljNdYLXLzjWY9Apm': 'CP Cast',
    '59fUC0CFgoMfiLDXCuhjUM': 'Sinapse',
    '22Wgt4ASeaw8mmoqAWNUn1': 'Nerdcast',
    '0qfFcilKpNKkXy8TbZ4moP': 'Scicast'
}

HISTORY_FILE = 'played_history.json'
EPISODES_HISTORY_FILE = 'played_episodes.json'
SONGS_TO_ADD = 120
FUSO_BR = timezone(timedelta(hours=-3))

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f: return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f: json.dump(history, f, indent=4)

def load_episodes_history():
    if os.path.exists(EPISODES_HISTORY_FILE):
        with open(EPISODES_HISTORY_FILE, 'r') as f: return json.load(f)
    return []

def save_episodes_history(history_list):
    with open(EPISODES_HISTORY_FILE, 'w') as f: json.dump(history_list, f, indent=4)

def ordenar_com_intervalo_artista(tracks, intervalo=15):
    arranged = []
    pool = tracks.copy()
    
    while pool:
        recent_artists = [t[2] for t in arranged[-intervalo:]]
        candidates = [t for t in pool if t[2] not in recent_artists]
        
        if candidates:
            candidate = random.choice(candidates)
        else:
            candidate = random.choice(pool)
            
        arranged.append(candidate)
        pool.remove(candidate)
        
    return arranged

def obter_noticia_diaria(sp, show_id):
    try:
        results = sp.show_episodes(show_id, limit=1, market='BR')
        if results and results['items']:
            ep = results['items'][0]
            data_lancamento = datetime.strptime(ep['release_date'][:10], '%Y-%m-%d').date()
            hoje = datetime.now(FUSO_BR).date()
            if data_lancamento >= hoje:
                return ep['uri']
    except Exception as e:
        nome = NOMES_PODCASTS.get(show_id, show_id)
        print(f"Error in news podcast {nome}: {e}")
    return None

def obter_episodio_rotativo(sp, show_id, episodios_tocados, palavra_ignorada=None):
    nome_exibicao = NOMES_PODCASTS.get(show_id, show_id)
    try:
        todos_episodios = []
        
        for offset in range(0, 1000, 50):
            results = sp.show_episodes(show_id, limit=50, offset=offset, market='BR')
            if not results or not results['items']: break
            todos_episodios.extend(results['items'])

        if not todos_episodios: return None

        episodios_validos = []
        for ep in todos_episodios:
            if palavra_ignorada and palavra_ignorada.lower() in ep['name'].lower(): continue
            episodios_validos.append(ep)

        episodios_validos.sort(key=lambda x: x['release_date'])

        for ep in episodios_validos:
            if ep['uri'] not in episodios_tocados:
                return ep['uri']
                
        print(f"  [!] Podcast {nome_exibicao} has no new episodes (you have heard the 1000 most recent).")
    except Exception as e:
        print(f"  [Error] Failed to read podcast {nome_exibicao}: {e}")
    return None

def obter_jesus_do_dia(sp, show_id, palavra_chave):
    try:
        results = sp.show_episodes(show_id, limit=5, market='BR')
        hoje = datetime.now(FUSO_BR).date()
        for ep in results['items']:
            if palavra_chave.lower() in ep['name'].lower():
                data_lancamento = datetime.strptime(ep['release_date'][:10], '%Y-%m-%d').date()
                if data_lancamento == hoje:
                    print(f"Found: {ep['name']} (Released today)")
                    return ep['uri']
        print("Warning: No 'Bom dia, Jesus!' episode posted today yet.")
    except Exception as e:
        print(f"Error fetching today's episode: {e}")
    return None

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI,
        scope="playlist-modify-public playlist-modify-private user-library-read", username=USERNAME
    ))

    now = datetime.now(FUSO_BR)
    
    day_of_week = (now.weekday() + 1) % 7
    welcome_results = sp.album_tracks(WELCOME_ALBUM_ID, limit=7)
    welcome_uri = f"spotify:track:{welcome_results['items'][day_of_week % len(welcome_results['items'])]['id']}"

    if now.hour == 0:
        print("Midnight Mode: Updating intro...")
        curr = sp.playlist_items(PLAYLIST_ID, limit=100)
        uris = [item['track']['uri'] for item in curr['items']]
        if uris: sp.playlist_replace_items(PLAYLIST_ID, [welcome_uri] + uris[1:])
        return

    print("Morning Mode: Full update started...")
    
    history = load_history()
    episodios_tocados = load_episodes_history()

    potential_tracks = []
    for offset in range(0, 1000, 50):
        res = sp.current_user_saved_tracks(limit=50, offset=offset)
        if not res['items']: break
        potential_tracks.extend([item['track'] for item in res['items']])

    def filter_tracks(track_list, hist):
        filtered = []
        seen = set()
        for t in track_list:
            raw_name = t['name'].strip().lower()
            artist_name = t['artists'][0]['name'].strip().lower()
            
            chave_unica = f"{raw_name} | {artist_name}"
            
            if chave_unica not in hist and raw_name not in hist and chave_unica not in seen:
                filtered.append((t['id'], raw_name, t['artists'][0]['name']))
                seen.add(chave_unica)
        return filtered

    filtered_tracks = filter_tracks(potential_tracks, history)
    
    QTD_REC = 20
    QTD_CUR = SONGS_TO_ADD - QTD_REC

    if len(filtered_tracks) < QTD_CUR:
        print("Low stock of unplayed songs! Resetting history...")
        history = {} 
        filtered_tracks = filter_tracks(potential_tracks, history)

    curtidas_selecionadas = random.sample(filtered_tracks, min(len(filtered_tracks), QTD_CUR))

    print(f"Fetching {QTD_REC} Hidden Gems...")
    recomendadas_selecionadas = []
    
    artistas_base = [t['artists'][0]['id'] for t in potential_tracks if t.get('artists') and t['artists'][0].get('id')]
    artistas_base = list(set(artistas_base))
    random.shuffle(artistas_base)

    chaves_minha_biblioteca = [f"{pt['name'].strip().lower()} | {pt['artists'][0]['name'].strip().lower()}" for pt in potential_tracks]

    for a_id in artistas_base:
        if len(recomendadas_selecionadas) >= QTD_REC: break
        try:
            tops = sp.artist_top_tracks(a_id, country='BR')
            if not tops or not tops.get('tracks'): continue
            random.shuffle(tops['tracks'])
            
            for track in tops['tracks']:
                raw_n = track['name'].strip().lower()
                artist_n = track['artists'][0]['name'].strip().lower()
                chave_unica = f"{raw_n} | {artist_n}"
                
                chaves_recomendadas = [f"{r[1]} | {r[2].strip().lower()}" for r in recomendadas_selecionadas]
                
                if chave_unica not in history and raw_n not in history and chave_unica not in chaves_minha_biblioteca and chave_unica not in chaves_recomendadas:
                    recomendadas_selecionadas.append((track['id'], raw_n, track['artists'][0]['name']))
                    break
        except Exception:
            continue

    todas_musicas = curtidas_selecionadas + recomendadas_selecionadas
    random.shuffle(todas_musicas)
    playlist_tracks = ordenar_com_intervalo_artista(todas_musicas, intervalo=15)

    ep1 = obter_noticia_diaria(sp, PODCAST_1_ID)
    ep2 = obter_noticia_diaria(sp, PODCAST_2_ID)
    ep_jesus = obter_jesus_do_dia(sp, INTELIGENCIA_LTDA_ID, "Bom dia, Jesus!")
    
    print("\nSpinning the Rotating Podcast roulette...")
    dias_p = (now.date() - datetime(2024, 1, 1).date()).days
    indice_base = dias_p % len(PODCASTS_ROTATIVOS)
    ep3 = None
    
    for offset in range(len(PODCASTS_ROTATIVOS)):
        idx = (indice_base + offset) % len(PODCASTS_ROTATIVOS)
        id_rot = PODCASTS_ROTATIVOS[idx]
        
        palavra_proibida = "Bom dia, Jesus!" if id_rot == INTELIGENCIA_LTDA_ID else None
        uri = obter_episodio_rotativo(sp, id_rot, episodios_tocados, palavra_ignorada=palavra_proibida)
        
        if uri:
            ep3 = uri
            nome_sucesso = NOMES_PODCASTS.get(id_rot, id_rot)
            print(f"-> SUCCESS! Slot 3 filled by {nome_sucesso}.\n")
            break

    final_uris = [welcome_uri]
    m_uris = [f"spotify:track:{t[0]}" for t in playlist_tracks]

    fila_podcasts = []
    if not ep1 or not ep2:
        if ep_jesus: fila_podcasts.append(ep_jesus)
        if ep1: fila_podcasts.append(ep1) 
        if ep2: fila_podcasts.append(ep2) 
    else:
        if ep1: fila_podcasts.append(ep1)
        if ep2: fila_podcasts.append(ep2)
        if ep_jesus: fila_podcasts.append(ep_jesus)

    slot1 = fila_podcasts[0] if len(fila_podcasts) > 0 else None
    slot2 = fila_podcasts[1] if len(fila_podcasts) > 1 else None
    slot3 = fila_podcasts[2] if len(fila_podcasts) > 2 else None

    final_uris.extend(m_uris[0:5])
    if slot1: final_uris.append(slot1)

    final_uris.extend(m_uris[5:20])
    if slot2: final_uris.append(slot2)

    final_uris.extend(m_uris[20:35])
    if slot3: final_uris.append(slot3)

    final_uris.extend(m_uris[35:110])
    
    if ep3:
        final_uris.append(ep3)
        episodios_tocados.append(ep3)
        
    final_uris.extend(m_uris[110:])

    sp.playlist_replace_items(PLAYLIST_ID, final_uris[:100])
    if len(final_uris) > 100: sp.playlist_add_items(PLAYLIST_ID, final_uris[100:200])
    
    for t in playlist_tracks: 
        chave_unica = f"{t[1]} | {t[2].strip().lower()}"
        history[chave_unica] = now.isoformat()
        
    save_history(history)
    save_episodes_history(episodios_tocados)
    
    print("Success! Morning radio updated!")

if __name__ == '__main__':
    main()