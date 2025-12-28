import itertools
import string
from difflib import SequenceMatcher

def get_similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def generate_variations(base_word, include_numbers=True, include_special=True):
    """Generate common password variations from a base word"""
    variations = []
    
    # Original word
    variations.append(base_word)
    variations.append(base_word.lower())
    variations.append(base_word.upper())
    variations.append(base_word.capitalize())
    
    if include_numbers:
        # Common number substitutions
        substitutions = {
            'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 
            'o': ['0'], 's': ['5', '$'], 't': ['7'], 'l': ['1']
        }
        
        # Apply substitutions
        temp = base_word.lower()
        for char, subs in substitutions.items():
            for sub in subs:
                variations.append(temp.replace(char, sub))
        
        # Add common number suffixes
        for num in ['123', '1', '12', '2024', '2025', '!', '!!', '123!']:
            variations.append(base_word + num)
            variations.append(base_word.lower() + num)
            variations.append(base_word.capitalize() + num)
    
    if include_special:
        # Add special character variations
        for char in ['!', '@', '#', '$']:
            variations.append(base_word + char)
            variations.append(char + base_word)
    
    return list(set(variations))  # Remove duplicates

def password_guesser():
    """Main function to help recover password"""
    print("=" * 60)
    print("PASSWORD RECOVERY HELPER")
    print("=" * 60)
    print("\nThis tool helps you remember passwords using context clues.")
    print("Note: Only use this for YOUR OWN accounts!\n")
    
    # Gather account information
    print("Let's gather some information about the account:\n")
    
    account_type = input("What type of account? (email, social media, etc.): ").strip()
    username = input("Username/Email: ").strip()
    
    # Gather password hints
    print("\n--- PASSWORD CLUES ---")
    print("Think about what the password might be related to:\n")
    
    related_word = input("What word is most closely related to the password? ").strip()
    
    print("\nOther possible hints:")
    pet_name = input("Pet name (press Enter to skip): ").strip()
    birth_year = input("Birth year or important year (press Enter to skip): ").strip()
    favorite_thing = input("Favorite thing/hobby (press Enter to skip): ").strip()
    memorable_place = input("Memorable place (press Enter to skip): ").strip()
    
    # Collect all hints
    hints = [related_word, pet_name, favorite_thing, memorable_place]
    hints = [h for h in hints if h]  # Remove empty strings
    
    print("\n" + "=" * 60)
    print("GENERATING PASSWORD CANDIDATES")
    print("=" * 60)
    
    all_candidates = []
    
    # Generate variations for each hint
    for hint in hints:
        variations = generate_variations(hint)
        all_candidates.extend(variations)
        
        # Combine with birth year if provided
        if birth_year:
            for var in variations[:10]:  # Limit combinations
                all_candidates.append(var + birth_year)
                all_candidates.append(birth_year + var)
    
    # Combine two hints
    if len(hints) >= 2:
        for combo in itertools.combinations(hints[:3], 2):
            combined = ''.join(combo)
            all_candidates.extend(generate_variations(combined, False, False)[:5])
    
    # Remove duplicates and sort by relevance
    all_candidates = list(set(all_candidates))
    
    # Sort by similarity to the main hint
    all_candidates.sort(key=lambda x: get_similarity(x, related_word), reverse=True)
    
    print(f"\nGenerated {len(all_candidates)} password candidates\n")
    print("Top 30 most likely passwords based on your hints:\n")
    
    for i, candidate in enumerate(all_candidates[:30], 1):
        print(f"{i:2d}. {candidate}")
    
    print("\n" + "=" * 60)
    print("\nTips:")
    print("- Try variations with different capitalizations")
    print("- Try adding special characters at the end (!,@,#)")
    print("- Try adding numbers like 123, your birth year, or current year")
    print("- Combine multiple words from your hints")
    
    # Option to see more
    show_more = input("\nShow all candidates? (y/n): ").strip().lower()
    if show_more == 'y':
        print("\n--- ALL CANDIDATES ---\n")
        for i, candidate in enumerate(all_candidates, 1):
            print(f"{i}. {candidate}")
            if i % 20 == 0:
                cont = input("\nPress Enter to continue or 'q' to quit: ")
                if cont.lower() == 'q':
                    break
    
    print("\n" + "=" * 60)
    print("IMPORTANT SECURITY REMINDER")
    print("=" * 60)
    print("✓ Only use this for YOUR OWN accounts")
    print("✓ Consider using a password manager for the future")
    print("✓ Enable two-factor authentication when possible")
    print("=" * 60)

if __name__ == "__main__":
    try:
        password_guesser()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
