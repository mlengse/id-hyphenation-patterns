
import re

def clean_file(input_path, output_path):
    # Patterns that indicate a corrupted line (likely icon names or UI elements)

    poison_patterns = [
        r'-outline',
        r'-sharp',
        r'react-',
        r'chevron-',
        r'arrow-',
        r'thumbs-up',
        r'thumbs-down',
        # Specific icon terms usually English
        r'battery-(?!$)',
        r'bookmark-',
        r'calendar-',
        r'clipboard-',
        r'cloud-',
        r'document-(?!$)', 
        r'flashlight-',
        r'game-controller',
        r'headset-',
        r'hourglass-',
        r'layers-',
        r'navigate-',
        r'notifications-',
        r'paper-plane',
        r'pie-chart',
        r'pricetag-',
        r'push-notification',
        r'reader-',
        r'receipt-',
        r'refresh-',
        r'reload-',
        r'reorder-',
        r'repeat-',
        r'resize-',
        r'rocket-',
        r'search-',
        r'server-',
        r'settings-',
        r'share-',
        r'shuffle-',
        r'speedometer-',
        r'stopwatch-',
        r'storefront-',
        r'telescope-',
        r'tennisball-',
        r'terminal-',
        r'thermometer-',
        r'videocam-',
        r'volume-(High|low|medium|off|mute)',
        r'wallet-',
        r'logo-',
        r'-circle',
    ]

    
    # Compile regex for performance
    poison_regex = re.compile('|'.join(poison_patterns), re.IGNORECASE)
    
    # Whitelist to rescue incorrectly flagged words
    whitelist_patterns = [
        r'logo-logo',
        r'ion-ion',
        r'radio-radio',
        r'menu-menu',
        r'pion-pion',
        r'bion-',
        r'stadion-',
        r'lampion-',
        r'milyon-',
        r'trilyon-',
        r'batalyon-',
    ]
    whitelist_regex = re.compile('|'.join(whitelist_patterns), re.IGNORECASE)
    
    kept_count = 0
    removed_count = 0
    removed_samples = []


    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out, \
         open('removed_lines.txt', 'w', encoding='utf-8') as f_removed:
        for line in f_in:
            line_content = line.strip()
            if not line_content:
                continue
                
            # Check for poison patterns
            if poison_regex.search(line_content):
                # Check whitelist
                if whitelist_regex.search(line_content):
                    f_out.write(line)
                    kept_count += 1
                    continue
                
                removed_count += 1
                f_removed.write(line_content + '\n')
                continue

            
            # Additional heuristic: If the key part (before :) contains unusual characters or looks like a camelCased variable
            parts = line_content.split(':', 1)
            if len(parts) > 0:
                key = parts[0].strip()
                # Check for CamelCase which is rare in standard Indonesian dictionary forms (usually lower case or hyphenated)
                # But be careful not to delete legitimate entries if any exist (though KBBI is usually lowercase)
                # Also check for very long words without hyphens might be suspicious if they contain english words
                pass

            f_out.write(line)
            kept_count += 1

    print(f"Finished cleaning.")
    print(f"Kept lines: {kept_count}")
    print(f"Removed lines: {removed_count}")
    print("\nSample removed lines:")
    for sample in removed_samples:
        print(sample)

if __name__ == "__main__":
    input_file = "kbbi_pemenggalan.txt"
    output_file = "kbbi_pemenggalan_clean.txt"
    clean_file(input_file, output_file)
