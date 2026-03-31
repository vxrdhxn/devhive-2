from backend.services.chunking import chunking_service

# Case that would cause infinite loop in old code:
# boundary at 10, chunk_overlap at 150.
# next_start = 10 - 150 = -140.
# In old code, start becomes -140, which is < text_length, so it repeats.
# And text.rfind(" ", -140, 660) finds the same space at 10.

text = "a" * 10 + " " + "b" * 989
print(f"Testing with text length {len(text)}")
try:
    print("Starting chunking...")
    # chunk_size=800, chunk_overlap=150
    chunks = chunking_service.chunk_text(text, chunk_size=800, chunk_overlap=150)
    print(f"Done! {len(chunks)} chunks found.")
    for i, c in enumerate(chunks):
        print(f"Chunk {i}: {len(c)} chars")
except Exception as e:
    print(f"Failed: {e}")
