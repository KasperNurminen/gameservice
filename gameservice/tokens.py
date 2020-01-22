from hashlib import md5


checksumstr = f"pid={pid:s}&sid={sid:s}&amount={amount:.2f}&token={secret:s}"
checksum = md5(checksumstr.encode('utf-8')).hexdigest()