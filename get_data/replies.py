
import pandas as pd
import os
import subprocess

# Step 1: Membaca file tweets.xlsx dengan header pada baris ke-4 (index 4)
file_path = 'tweet_full.xlsx'
df_tweets = pd.read_excel(file_path, header=4)

# Step 2: Ambil value baris pertama kolom 'Name' dan simpan sebagai account_name
# Hitung jumlah data
account_name = df_tweets['Name'].iloc[0]
data_length = len(df_tweets)

print(f"Account Name: {account_name}")
print(f"Total Data: {data_length}")
print(f"\nKolom yang tersedia: {df_tweets.columns.tolist()}")

# Step 3: Perulangan untuk melakukan scraping
# Inisialisasi DataFrame untuk menampung semua replies
df_main = pd.DataFrame()

# Ambil token dari environment variable
twitter_auth_token = os.environ.get('TWITTER_AUTH_TOKEN')

if twitter_auth_token is None:
    print("\nError: TWITTER_AUTH_TOKEN environment variable tidak ditemukan!")
    print("Pastikan Anda sudah set: export TWITTER_AUTH_TOKEN='your_token_here'")
else:
    # Loop untuk setiap baris di df_tweets
    for index, row in df_tweets.iterrows():
        try:
            print(f"\n{'='*60}")
            print(f"Processing tweet {index + 1}/{data_length}")
            print(f"{'='*60}")
            
            # Ambil nilai Replies (jumlah balasan)
            reply_count = int(row['Replies']) if pd.notna(row['Replies']) else 0
            
            # Gunakan Permalink untuk extract ID tweet
            # Format: https://www.twitter.com/account/status/ID_TWEET
            permalink = row['Permalink']
            tweet_id = permalink.split('/')[-1] if permalink else f"tweet_{index}"
            
            print(f"Tweet ID: {tweet_id}")
            print(f"Replies: {reply_count}")
            print(f"Caption: {row['Caption'][:100] if pd.notna(row['Caption']) else 'N/A'}...")
            
            # Nama file untuk menyimpan replies
            filename = f"{tweet_id}_replies.csv"
            
            # Command untuk menjalankan tweet-harvest
            command = (
                f"npx -y tweet-harvest@2.6.1 -o {filename} "
                f"-s \"conversation_id:{tweet_id}\" "
                f"--token \"{twitter_auth_token}\" "
                f"--limit {reply_count + 10}"
            )
            
            print(f"\nExecuting: tweet-harvest untuk tweet ID {tweet_id}...")
            
            # Jalankan command
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✓ Berhasil mengambil data untuk tweet ID: {tweet_id}")
                
                # Baca CSV yang baru dibuat
                csv_path = f"tweets-data/{filename}"
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path, delimiter=",")
                    
                    # Tambahkan kolom reply_to_tweet_id
                    df['reply_to_tweet_id'] = tweet_id
                    
                    # Concat dengan df_main
                    df_main = pd.concat([df_main, df], axis=0, ignore_index=True, sort=False)
                    
                    print(f"✓ Data berhasil ditambahkan ke df_main. Total rows: {len(df_main)}")
                else:
                    print(f"✗ File {csv_path} tidak ditemukan!")
            else:
                print(f"✗ Error saat menjalankan tweet-harvest:")
                print(f"Return Code: {result.returncode}")
                if result.stderr:
                    print(f"STDERR: {result.stderr[:200]}")
                if result.stdout:
                    print(f"STDOUT: {result.stdout[:200]}")
        
        except subprocess.TimeoutExpired:
            print(f"✗ Timeout saat memproses tweet {index + 1}")
            continue
        except Exception as e:
            print(f"✗ Error pada baris {index + 1}: {str(e)}")
            continue
    
    # Simpan hasil scraping ke CSV
    if len(df_main) > 0:
        output_file = f"tweets-data/{account_name}_all_replies.csv"
        df_main.to_csv(output_file, index=False)
        print(f"\n{'='*60}")
        print(f"✓ Scraping selesai!")
        print(f"✓ Total replies: {len(df_main)}")
        print(f"✓ Data tersimpan di: {output_file}")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"⚠ Tidak ada data yang berhasil dikumpulkan")
        print(f"{'='*60}")