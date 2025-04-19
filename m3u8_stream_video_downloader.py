import argparse
from urllib.parse import urljoin
import requests
from m3u8 import M3U8

def download_m3u8(url, output_file):
    # Fetch the initial playlist
    response = requests.get(url)
    if not response.ok:
        print(f"Failed to fetch the initial playlist: HTTP {response.status_code}")
        return False

    # Parse the initial playlist with correct base URI
    base_uri = urljoin(url, '.')
    playlist = M3U8(content=response.text, base_uri=base_uri)

    # Handle master playlist by selecting the best quality
    if playlist.is_variant:
        print("Master playlist detected. Selecting the best quality...")
        best_playlist = max(playlist.playlists, key=lambda p: p.stream_info.bandwidth)
        best_playlist_url = best_playlist.absolute_uri
        print(f"Fetching {best_playlist_url}...")
        response_best = requests.get(best_playlist_url)
        if not response_best.ok:
            print(f"Failed to fetch best quality playlist: HTTP {response_best.status_code}")
            return False
        media_base_uri = urljoin(best_playlist_url, '.')
        media_playlist = M3U8(content=response_best.text, base_uri=media_base_uri)
    else:
        media_playlist = playlist

    # Download all segments
    total_segments = len(media_playlist.segments)
    print(f"Downloading {total_segments} segments...")
    
    with open(output_file, 'wb') as f:
        for idx, segment in enumerate(media_playlist.segments):
            segment_url = segment.absolute_uri
            print(f"Downloading segment {idx + 1}/{total_segments}: {segment_url}")
            segment_response = requests.get(segment_url)
            if segment_response.ok:
                f.write(segment_response.content)
                f.flush()
            else:
                print(f"Failed to download segment {idx + 1}: HTTP {segment_response.status_code}")
    
    print("Download completed successfully.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download an HLS stream from an M3U8 URL.")
    parser.add_argument("url", help="URL of the M3U8 playlist")
    parser.add_argument("output", help="Output file name (e.g., video.ts)")
    args = parser.parse_args()
    
    if not download_m3u8(args.url, args.output):
        print("Download failed.")

