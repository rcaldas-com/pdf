import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_cargo_section(text, cargo_start, cargo_end):
    start_index = text.find(cargo_start)
    end_index = text.find(cargo_end, start_index)
    if start_index == -1 or end_index == -1:
        return None
    
    # Find the end of the line containing cargo_start
    start_index = text.find('\n', start_index) + 1

    # Find the correct start line that begins with a number (registration number)
    while start_index < len(text):
        line_end = text.find('\n', start_index)
        if line_end == -1:
            break
        line = text[start_index:line_end].strip()
        if line and line[0].isdigit() and ',' in line:
            break
        start_index = line_end + 1

    # Find the start of the line containing cargo_end
    end_index = text.rfind('\n', 0, end_index)
    
    return text[start_index:end_index]

def parse_candidates(cargo_section):
    candidates = []
    # Remove all line breaks to make it a single line of text
    cargo_section = cargo_section.replace('\n', ' ')
    # Split the text by "/"
    parts = cargo_section.split('/')
    for part in parts:
        fields = part.split(',')
        if len(fields) >= 8:
            try:
                registration_number = fields[0].strip()
                name = fields[1].strip()
                p1_score = float(fields[2].strip().replace(' ', ''))
                p1_correct = int(fields[3].strip().replace(' ', ''))
                p2_score = float(fields[4].strip().replace(' ', ''))
                p2_correct = int(fields[5].strip().replace(' ', ''))
                final_score = float(fields[6].strip().replace(' ', ''))
                p3_score_str = fields[7].strip().replace(' ', '').replace(',', '.')
                if p3_score_str.endswith('.'):
                    p3_score_str = p3_score_str[:-1]
                p3_score = float(p3_score_str)
                total_score = final_score + p3_score
                candidates.append({
                    'registration_number': registration_number,
                    'name': name,
                    'p1_score': p1_score,
                    'p1_correct': p1_correct,
                    'p2_score': p2_score,
                    'p2_correct': p2_correct,
                    'final_score': final_score,
                    'p3_score': p3_score,
                    'total_score': total_score
                })
            except ValueError:
                print('Error parsing fields:', fields)
                continue
    return candidates


def main():
    pdf_path = 'STJ.pdf'
    cargo_start = 'CARGO 18:'
    cargo_end = 'Resultado final dos candidatos que solicitaram concorrer'

    text = extract_text_from_pdf(pdf_path)
    cargo_section = extract_cargo_section(text, cargo_start, cargo_end)

    if cargo_section:
        candidates = parse_candidates(cargo_section)
        sorted_candidates = sorted(candidates, key=lambda x: x['total_score'], reverse=True)
        
        for i, candidate in enumerate(sorted_candidates, start=1):
            print(f"{i}. {candidate['name']} - Total Score: {candidate['total_score']}")
    else:
        print('Cargo section not found.')

if __name__ == '__main__':
    main()