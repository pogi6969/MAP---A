// Introduction and Methodology paper (narrowed study).
// usage: node im_paper.js out.docx
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, Footer, PageNumber, TabStopType,
  Table, TableRow, TableCell, WidthType, ShadingType, VerticalAlign, BorderStyle,
} = require('docx');
const h = require('./lib');

const { C, L, B, I } = h;
const TITLE = 'Enhancing the Filipino Word Recognition of Grade 2 Frustration-Level Readers Through Syllable-Based Reading Intervention Materials (RIM) in Albay Central School';

// ---------- header ----------
const ctr = (text, style = {}) => h.np([[text, style]], { align: C, line: 240, after: 0 });
const header = [
  ctr('BICOL COLLEGE'), ctr('Daraga, Albay'), ctr('Graduate School'),
  new Paragraph({ alignment: C, spacing: { after: 0, line: 240 }, children: [new TextRun('1'), new TextRun({ text: 'st', superScript: true }), new TextRun(' Sem AY 2026-27')] }),
  ...h.blank(1), ctr('MEd Curriculum Instruction', B), ctr('Research Methods in Education', B), ...h.blank(2),
  new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: h.W }], spacing: { after: 0 },
    children: [new TextRun({ text: 'Irene A. Loria', bold: true }), new TextRun({ text: '\tProfessor: Dr. Manny B. Macabeo', bold: true })],
  }),
  ...h.blank(2),
  h.np('Research Title:', { align: L, line: 240, after: 200 }),
  h.np([[TITLE, B]], { align: C, line: 276, after: 0 }),
  ...h.blank(1),
];
const section = (title, pageBreak = false) => h.np([[title, B]], { align: C, before: 240, after: 200, keepNext: true, pageBreakBefore: pageBreak });

// ---------- conceptual paradigm (table-based so it stays editable) ----------
const line = { style: BorderStyle.SINGLE, size: 8, color: '000000' };
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const cellP = (text, o = {}) => new Paragraph({
  alignment: o.align || C, keepNext: true, spacing: { after: o.after || 0, line: 240, lineRule: 'auto' },
  children: [new TextRun({ text, bold: o.bold, size: o.size || 19 })],
});
const box = (w, paras, o = {}) => new TableCell({
  borders: o.border === false ? { top: none, bottom: none, left: none, right: none } : { top: line, bottom: line, left: line, right: line },
  width: { size: w, type: WidthType.DXA }, columnSpan: o.span,
  shading: o.shade ? { fill: o.shade, type: ShadingType.CLEAR, color: 'auto' } : undefined,
  margins: { top: 80, bottom: 80, left: 100, right: 100 },
  verticalAlign: o.top ? VerticalAlign.TOP : VerticalAlign.CENTER, children: paras,
});
const bullets = (items) => items.map((t) => cellP(`• ${t}`, { align: L, after: 60 }));
const ipo = () => {
  const w = h.scale([30, 4, 32, 4, 30]);
  const arrow = (i) => box(w[i], [cellP('▶', { size: 28 })], { border: false });
  const head = (i, t) => box(w[i], [cellP(t, { bold: true, size: 21 })], { shade: 'D9D9D9' });
  const empty = (i) => box(w[i], [cellP('')], { border: false });
  return new Table({
    width: { size: h.W, type: WidthType.DXA }, columnWidths: w,
    rows: [
      new TableRow({ cantSplit: true, children: [head(0, 'INPUT'), empty(1), head(2, 'PROCESS'), empty(3), head(4, 'OUTPUT')] }),
      new TableRow({ cantSplit: true, children: [
        box(w[0], bullets([
          'Pre-test word recognition of the Grade 2 frustration-level readers in CV-CV words, CV-CVC words, and three-syllable words',
          'Letter-sound knowledge of the learners (at least 15 of 20 letter sounds)',
          'Syllable-Based Reading Intervention Materials (RIM) in three modules',
        ]), { top: true }),
        arrow(1),
        box(w[2], bullets([
          'Screening of learners for letter-sound knowledge',
          'Validation and pilot testing of the Filipino Word Recognition Test',
          'Pre-test (Form A)',
          'Six-week intervention: 24 small-group sessions using the RIM',
          'Post-test (Form B)',
          'Descriptive statistics, Shapiro–Wilk test, paired-samples t-test, and Cohen’s d',
        ]), { top: true }),
        arrow(3),
        box(w[4], bullets([
          'Enhanced word recognition of the learners in the three syllable patterns',
          'Evidence on whether, and in which syllable patterns, the Syllable-Based RIM enhances word recognition',
        ]), { top: true }),
      ] }),
      new TableRow({ cantSplit: true, children: [box(h.W, [cellP('◀————————  FEEDBACK  ————————')], { span: 5, border: false })] }),
    ],
  });
};

// ---------- test items ----------
const FORM_A = {
  cvcv: ['bata', 'mesa', 'puno', 'bola', 'saya', 'lobo', 'kama', 'tasa', 'sako', 'pusa', 'lata', 'dila', 'baka', 'bote', 'mata'],
  cvcvc: ['bahay', 'lapis', 'sabon', 'tubig', 'gatas', 'dagat', 'bukid', 'kahon', 'lamok', 'bigas', 'sipit', 'buhok', 'takip', 'bunot', 'papel'],
  three: ['masaya', 'kabayo', 'kamote', 'palaka', 'kalesa', 'pitaka', 'balita', 'makina', 'kalabaw', 'halaman', 'malinis', 'sapatos', 'matamis', 'bukirin', 'salamin'],
};
const FORM_B = {
  cvcv: ['baso', 'bibe', 'gabi', 'mani', 'sapa', 'tela', 'kubo', 'pato', 'buko', 'damo', 'bago', 'lima', 'sili', 'tuta', 'tubo'],
  cvcvc: ['kamay', 'palad', 'manok', 'dahon', 'sapin', 'bukas', 'gulay', 'hapon', 'sukat', 'lubid', 'bulak', 'kalan', 'tulog', 'sibat', 'basag'],
  three: ['kabibe', 'mabuti', 'bulati', 'lalaki', 'dalaga', 'sabado', 'buwaya', 'manika', 'malamig', 'masipag', 'kamatis', 'tinapay', 'katawan', 'palayok', 'kalamay'],
};
const itemRows = [
  ['Two-syllable words with open syllables (CV-CV)', FORM_A.cvcv.join(', '), FORM_B.cvcv.join(', ')],
  ['Two-syllable words with a closed final syllable (CV-CVC)', FORM_A.cvcvc.join(', '), FORM_B.cvcvc.join(', ')],
  ['Three-syllable words (8 CV-CV-CV and 7 CV-CV-CVC)', FORM_A.three.join(', '), FORM_B.three.join(', ')],
];

const body = [
  ...header,

  // ===================== INTRODUCTION =====================
  section('INTRODUCTION'),
  h.h2('Background of the Study'),
  h.p('Reading begins with words. Before children can understand sentences and stories, they must first be able to recognize the words on the page accurately and quickly. Word recognition, the ability to read words either by decoding their letter-sound patterns or by retrieving them instantly from memory, is the foundation on which reading fluency and comprehension are built (Ehri, 2005). The Simple View of Reading expresses this relationship clearly: reading comprehension is the product of decoding and language comprehension, so a child who cannot decode the words of a text cannot understand it, however well the child understands spoken language (Gough & Tunmer, 1986; Hoover & Gough, 1990). When word recognition becomes automatic, the reader’s limited attention is freed for understanding meaning (LaBerge & Samuels, 1974). Securing word recognition is therefore the first task of reading instruction in the early grades.'),
  h.p('Children who fail to acquire word recognition early rarely catch up on their own. Juel (1988) found that a child who was a poor reader at the end of Grade 1 had an 88 percent probability of remaining a poor reader at the end of Grade 4. Stanovich (1986) described the widening gap that follows as the “Matthew effect” in reading: children who read well read more and grow stronger, while children who struggle read less and fall further behind. Torgesen (2004) argued that the most effective way to prevent this downward spiral is early, intensive, and systematic intervention that targets the specific skills struggling readers lack.'),
  h.p('In the Philippines, the challenge of early reading is well documented. Filipino 15-year-old learners obtained the lowest mean reading score among 79 participating countries and economies in the 2018 Programme for International Student Assessment (OECD, 2019) and remained among the lowest performers in 2022 (OECD, 2023). The 2019 Southeast Asia Primary Learning Metrics found that only 10 percent of Filipino Grade 5 learners reached the minimum reading proficiency expected at the end of primary school (UNICEF & SEAMEO, 2020), and the World Bank (2022) placed the country’s learning poverty rate at about 91 percent. The Department of Education (DepEd) has responded with a series of initiatives, including the “Hamon: Bawat Bata Bumabasa” campaign (Department of Education, 2019), the National Learning Recovery Program (Department of Education, 2023), Catch-Up Fridays (Department of Education, 2024a), and the MATATAG Curriculum (Department of Education, 2024b), while Republic Act No. 12028 (2024), or the Academic Recovery and Accessible Learning (ARAL) Program Act, institutionalized tutorial support in reading for learners who lag behind.'),
  h.p('These national efforts, however, can succeed only if classroom interventions are precise. Struggling readers are not a uniform group. Some have not yet learned the sounds of the letters; others know the letter sounds but cannot blend them into syllables and words; still others decode accurately but slowly, or read fluently without understanding. Research on effective intervention shows that struggling readers benefit most from explicit and systematic instruction that targets the specific skill they lack (National Reading Panel, 2000; Wanzek & Vaughn, 2007). An intervention that tries to address every reading skill at once risks addressing none of them well, and a study that tries to measure every skill at once cannot show clearly what the intervention accomplished.'),
  h.p('For learners reading in Filipino, the most important bridge in early reading is the step from knowing letter sounds to reading whole words. Filipino has a relatively transparent orthography, in which letters correspond consistently to sounds, and its words are built from a small number of syllable patterns, chiefly open syllables that end in a vowel (CV, as in ba) and closed syllables that end in a consonant (CVC, as in bas). Children learning to read in transparent orthographies generally acquire accurate word reading much faster than children learning to read in a deep orthography such as English (Seymour et al., 2003). Ehri (2005) explained that readers become efficient when they move beyond sounding out letter by letter to recognizing larger units such as syllables, which they then bond to the spellings and pronunciations of words in memory. Teaching learners to blend sounds into syllables and syllables into words, beginning with open syllables and progressing to closed syllables and longer words, is therefore a natural and efficient route to word recognition in Filipino.'),
  h.p('At Albay Central School, the researcher has observed a distinct group of Grade 2 learners who have not made this transition. These learners can give the sounds of most letters, yet when they meet a printed word, they read it letter by letter (b-a-t-a) without blending the sounds into a word, read the first syllable and guess the rest, or stop altogether. Their difficulty is most evident in words with a closed final syllable, which they often read as if the syllable were open (for example, reading bahay as baha), and in three-syllable words, which they abandon after the first syllable. These learners are classified as reading at the frustration level in the beginning-of-the-year reading assessment, and because they cannot recognize words, they cannot read the sentences and texts used in their lessons. Each week that this difficulty persists, the gap between them and their classmates widens.'),
  h.p('In the researcher’s experience, the materials available for remediation serve this group poorly. Some focus on letter names and sounds, which these learners already know, while others move directly to sentences and passages, which these learners cannot yet read. What these learners need is sequenced, decodable practice that bridges the gap between letter sounds and word reading: practice that moves systematically from open syllables to closed syllables to three-syllable words, using only patterns that have already been taught (Mesmer, 2001). Teacher-developed materials, contextualized to the learners’ setting and validated before use, can provide this practice (Republic Act No. 10533, 2013; Tomlinson, 2011).'),
  h.p('This study therefore focuses on a single, clearly defined problem: the inability of Grade 2 frustration-level readers who already know most letter sounds to recognize Filipino words. To address it, the researcher will develop and use Syllable-Based Reading Intervention Materials (RIM), consisting of three modules that progress from two-syllable words with open syllables (CV-CV), to two-syllable words with a closed final syllable (CV-CVC), to three-syllable words, delivered in small-group sessions over six weeks. The study will measure the learners’ word recognition in each of these three syllable patterns before and after the intervention to determine whether, and in which patterns, the materials enhance word recognition. By limiting its focus to one skill, one group of learners, three syllable patterns, one school, and one quarter, the study aims to produce clear and usable evidence on whether a targeted, syllable-based intervention helps struggling readers cross the bridge from letter sounds to word reading.'),

  h.h2('Objectives of the Study'),
  h.p('This study aims to enhance the Filipino word recognition of Grade 2 frustration-level readers at Albay Central School through the use of Syllable-Based Reading Intervention Materials (RIM) during the third quarter of School Year 2026–2027.'),
  h.np('Specifically, it aims to:'),
  h.item('1.', 'Determine the word recognition level of the learners before the intervention (pre-test) in reading:'),
  ...h.list(['two-syllable words with open syllables (CV-CV);', 'two-syllable words with a closed final syllable (CV-CVC); and', 'three-syllable words.'], { style: 'alpha', level: 1, after: 0 }),
  h.item('2.', 'Determine the word recognition level of the learners after the intervention (post-test) in reading the same three syllable patterns.'),
  h.item('3.', 'Ascertain whether there is a significant difference between the pre-test and post-test word recognition levels of the learners in each syllable pattern and in overall word recognition.'),

  h.h2('Hypothesis'),
  h.p('The following null hypothesis will be tested at the .05 level of significance:'),
  h.para([['Ho: ', B], ['There is no significant difference between the pre-test and post-test word recognition levels of the Grade 2 frustration-level readers in reading two-syllable words with open syllables, two-syllable words with a closed final syllable, and three-syllable words, and in overall word recognition.']], { indent: { left: 720, right: 720 } }),

  h.h2('Theoretical and Conceptual Framework'),
  h.p('The study is anchored on Ehri’s (2005) phase theory of word reading. Ehri described how readers move from the partial alphabetic phase, in which they use only some letters to guess words, to the full alphabetic phase, in which they decode words by connecting all letters to sounds, and finally to the consolidated alphabetic phase, in which they recognize larger units such as syllables. Through repeated, accurate decoding, the spellings and pronunciations of words become bonded in memory, and words come to be recognized instantly. The learners in this study are at the boundary between the partial and full alphabetic phases: they know letter sounds but do not yet blend them reliably. The Syllable-Based RIM is designed to move them into the full and consolidated phases by teaching syllables as units of decoding.'),
  h.p('The study is supported by the automaticity theory of LaBerge and Samuels (1974), which explains why the study measures words recognized within three seconds rather than words eventually sounded out: only automatic word recognition frees attention for comprehension. The Simple View of Reading (Gough & Tunmer, 1986) explains why word recognition is a worthwhile target in itself, since comprehension cannot develop while decoding fails. Finally, Vygotsky’s (1978) Zone of Proximal Development and the related idea of scaffolding (Wood et al., 1976) guide the delivery of the RIM: each module begins slightly beyond what the learners can do alone, and the teacher’s support is reduced as they gain control of each syllable pattern.'),
  h.p('Figure 1 presents the conceptual paradigm of the study. The input consists of the pre-test word recognition of the learners in the three syllable patterns, their letter-sound knowledge, and the Syllable-Based RIM. The process covers the screening of learners, the validation of the test, the pre-test, the six-week intervention, the post-test, and the statistical analysis. The output is the enhanced word recognition of the learners and evidence on whether, and in which syllable patterns, the RIM is effective. The feedback loop indicates that the results will be used to refine the materials.'),
  h.gap(),
  ipo(),
  h.fcaption('Conceptual Paradigm of the Study'),

  h.h2('Significance of the Study'),
  h.p('The study is expected to benefit the following:'),
  h.runIn('Learners.', 'The Grade 2 frustration-level readers will receive targeted, systematic instruction in the exact skill they lack, the blending of sounds and syllables into words, which is the gateway to reading sentences and texts in all subjects.'),
  h.runIn('Teachers.', 'Grade 2 and other early-grade teachers will gain a validated, ready-to-use set of syllable-based materials and evidence on which syllable patterns their struggling readers find most difficult, which can guide their remedial reading sessions and Catch-Up Fridays.'),
  h.runIn('School Head and Reading Coordinator.', 'The results will provide a basis for deciding whether to adopt the Syllable-Based RIM as part of the school’s reading intervention program and how to group and schedule learners who are reading at the frustration level.'),
  h.runIn('Parents.', 'Parents will gain a clearer understanding of their children’s specific reading difficulty and simple syllable-based activities they can use to support reading at home.'),
  h.runIn('Learning Action Cell and Materials Developers.', 'The study offers a model of a narrowly focused, validated intervention material that can be reviewed, refined, and adapted for other grade levels and languages through the Learning Action Cell (Department of Education, 2016).'),
  h.runIn('Future Researchers.', 'The study provides a design, a validated instrument, and baseline evidence that can be extended to related questions, such as the effect of syllable-based instruction on reading fluency and comprehension, or its use with a comparison group.'),

  h.h2('Scope and Delimitation'),
  h.p('The study focuses on one skill, one group of learners, and one intervention, as summarized in Table 1.'),
  ...h.ntable('Scope of the Study', [24, 76], ['Aspect', 'Coverage'], [
    [{ text: 'Variable studied', bold: true }, 'Word recognition in Filipino: the accurate and automatic reading (within three seconds) of words presented in isolation'],
    [{ text: 'Syllable patterns', bold: true }, 'Two-syllable words with open syllables (CV-CV); two-syllable words with a closed final syllable (CV-CVC); three-syllable words (CV-CV-CV and CV-CV-CVC)'],
    [{ text: 'Subjects', bold: true }, 'Grade 2 learners of Albay Central School, School Year 2026–2027, who are reading at the frustration level and who can give at least 15 of the 20 letter sounds of the Abakada'],
    [{ text: 'Intervention', bold: true }, 'Syllable-Based Reading Intervention Materials (RIM): three modules, 24 sessions of 30 minutes, four times a week for six weeks, in small groups of three to five learners'],
    [{ text: 'Measure', bold: true }, 'Filipino Word Recognition Test, Forms A and B: 45 untaught words each, 15 per syllable pattern'],
    [{ text: 'Design and setting', bold: true }, 'One-group pretest–posttest design; Albay Central School; third quarter of School Year 2026–2027'],
    [{ text: 'Not covered', bold: true }, 'Learners who know fewer than 15 letter sounds; reading in English; reading of sentences and passages; reading fluency and comprehension; spelling and writing; long-term retention; evaluation of the materials by teachers'],
  ], { aligns: [L, L], size: 20, vTop: true }),
  h.p('The study is limited to word recognition because it is the specific skill that keeps these learners at the frustration level and because it can be measured precisely. It is limited to learners who already know most letter sounds so that the intervention addresses blending and syllable recognition, not letter learning; learners who know fewer letter sounds need a different intervention and will continue to receive the school’s regular remedial instruction. The study is limited to Filipino, the language in which these learners are learning to read, and to the three syllable patterns that make up most of the words in Grade 2 Filipino texts. Because it uses a one-group design in a single school, its findings will apply only to the Grade 2 frustration-level readers of Albay Central School and should not be generalized to other learners or schools without further study.'),

  h.h2('Definition of Terms'),
  h.p('The following terms are defined conceptually and operationally as they are used in this study:'),
  h.runIn('Automaticity.', 'This refers to the ability to perform a skill quickly and with little conscious effort (LaBerge & Samuels, 1974). In this study, it refers to the reading of a word correctly within three seconds of seeing it.'),
  h.runIn('Blending.', 'This refers to the combining of individual sounds or syllables to form a word. In this study, it refers to the learners’ joining of letter sounds into syllables and of syllables into Filipino words, the skill targeted by the Syllable-Based RIM.'),
  h.runIn('Closed Syllable.', 'This is a syllable that ends in a consonant sound. In this study, it refers to the CVC syllable at the end of two-syllable words such as bahay and lapis.'),
  h.runIn('Decoding.', 'This refers to the translation of printed letters into their corresponding sounds to identify a word (Gough & Tunmer, 1986). In this study, it refers to the process by which the learners read words by blending their sounds and syllables.'),
  h.runIn('Frustration-Level Readers.', 'These are learners for whom grade-level text is too difficult to read even with assistance (Department of Education, 2018). In this study, they are the Grade 2 learners of Albay Central School who are classified as reading at the frustration level in the beginning-of-the-year reading assessment and who can give at least 15 of the 20 letter sounds in the screening.'),
  h.runIn('Open Syllable.', 'This is a syllable that ends in a vowel sound. In this study, it refers to the CV syllables in two-syllable words such as bata and mesa.'),
  h.runIn('Pre-test and Post-test.', 'These are assessments given before and after an intervention to measure change in performance. In this study, they refer to Forms A and B of the Filipino Word Recognition Test, administered before and after the six-week intervention.'),
  h.runIn('Syllable.', 'This is a unit of spoken language consisting of a vowel sound, with or without surrounding consonants. In this study, it refers to the CV and CVC units used in the RIM as the building blocks of Filipino words.'),
  h.runIn('Syllable-Based Reading Intervention Materials (RIM).', 'These are instructional materials that teach word reading through syllables rather than individual letters. In this study, they are the teacher-developed syllable cards, syllable wheels, word-building tiles, decodable word lists, and decodable phrases and sentences organized into three modules: open syllables, closed final syllables, and three-syllable words.'),
  h.runIn('Syllable Pattern.', 'This refers to the arrangement of consonants and vowels in the syllables of a word. In this study, it refers to the three patterns measured: CV-CV, CV-CVC, and three-syllable words.'),
  h.runIn('Word Recognition.', 'This refers to the ability to read words accurately and quickly, either by decoding them or by retrieving them from memory (Ehri, 2005). In this study, it refers to the number of words in each syllable pattern of the Filipino Word Recognition Test that a learner reads correctly within three seconds.'),
  h.runIn('Word Recognition Level.', 'This refers to the descriptive level of a learner’s word recognition. In this study, it refers to the level (Proficient, Approaching Proficiency, Developing, or Beginning) that corresponds to the percentage of words read correctly in each syllable pattern.'),

  // ===================== METHODOLOGY =====================
  section('METHODOLOGY', true),
  h.p('This section presents the research design, the intervention, the research instrument, the data gathering procedures, the respondents, the sampling technique, the study site, the data analysis plan, and the ethical considerations of the study.'),

  h.h2('Research Design'),
  h.p('The study will use a quantitative, pre-experimental, one-group pretest–posttest design. In this design, a single group is measured on the dependent variable before and after exposure to a treatment, and the change between the two measurements is examined (Campbell & Stanley, 1963; Fraenkel et al., 2012). The group is the Grade 2 frustration-level readers of Albay Central School, the treatment is the Syllable-Based RIM, and the dependent variable is word recognition in three syllable patterns. The design is represented as follows:', { keepNext: true }),
  h.center([['O₁            X            O₂', B]], { before: 60, after: 60, keepNext: true }),
  h.np('where O₁ is the pre-test (Form A), X is the six-week intervention using the Syllable-Based RIM, and O₂ is the post-test (Form B).'),
  h.p('This design is the most appropriate for three reasons. First, the study asks whether the word recognition of the same learners improves after the intervention, which requires measuring each learner before and after. Second, the number of learners who meet the specific inclusion criteria in one school is small, which makes a separate, equivalent comparison group impractical. Third, withholding the intervention from learners who need it, solely to form a comparison group, would be ethically questionable, since reading difficulties left unaddressed in the early grades tend to persist (Juel, 1988; Torgesen, 2004).'),
  h.p('Because the design has no control group, it is vulnerable to threats to internal validity such as history, maturation, testing, and instrumentation (Campbell & Stanley, 1963). The study reduces these threats by (a) using equivalent test forms so that learners do not see the same words twice; (b) using only words that are not taught in the RIM, so that the post-test measures transfer to new words rather than memorization; (c) administering both tests under the same standardized conditions; (d) having a second rater score audio recordings without knowing whether they came from the pre-test or the post-test; (e) keeping the intervention short and clearly defined; and (f) reporting effect sizes and confidence intervals along with tests of significance. Since effect sizes from researcher-made tests over short periods tend to be larger than those from standardized tests (Cheung & Slavin, 2016), the results will be interpreted with this in mind.'),

  h.h2('The Intervention: Syllable-Based Reading Intervention Materials'),
  h.p('The Syllable-Based RIM consists of three modules, each focused on one syllable pattern and each building on the previous one, following the progression from the full to the consolidated alphabetic phase described by Ehri (2005). Table 2 presents the modules. None of the practice words in the RIM appears in the Filipino Word Recognition Test.'),
  ...h.ntable('Modules of the Syllable-Based Reading Intervention Materials', [17, 9, 22, 18, 34], ['Module', 'Weeks', 'Target Pattern and Content', 'Sample Practice Words', 'Materials and Activities'], [
    ['1. Bukas na Pantig (Open Syllables)', '1–2', 'Blending consonant and vowel sounds into CV syllables (ba, be, bi, bo, bu) and CV syllables into two-syllable words', 'baba, sabi, lagi, kuya, sipa', 'Syllable cards; syllable wheels; syllable chains; word building with syllable tiles; decodable word lists; word–picture matching'],
    ['2. Saradong Pantig (Closed Final Syllable)', '3–4', 'Adding a final consonant to form CVC syllables (pa–pag, sa–sap) and reading CV-CVC words', 'sabaw, bayad, likod, hinog, talon', 'Open–closed syllable contrast cards; word sorts (open or closed); decodable word lists; decodable phrases'],
    ['3. Salitang may Tatlong Pantig (Three-Syllable Words)', '5–6', 'Segmenting and blending three-syllable words of the CV-CV-CV and CV-CV-CVC patterns', 'bayani, tahanan, malakas, kulisap, malapit', 'Syllable clapping and counting; syllable slides; building words from known syllables; decodable sentences; “beat the clock” timed reading for automaticity'],
  ], { aligns: [L, C, L, L, L], size: 18, vTop: true }),
  h.p('The RIM will be used in 24 sessions of about 30 minutes, held four times a week for six weeks. Sessions will be scheduled, in coordination with the school head, during remedial reading time and Catch-Up Fridays so that learners do not miss regular instruction. Learners will work in small groups of three to five. Every session follows the same routine, presented in Table 3, which applies the gradual release of responsibility from teacher modeling to independent practice (Vygotsky, 1978; Wood et al., 1976).'),
  ...h.ntable('Structure of a RIM Session', [26, 12, 62], ['Phase', 'Minutes', 'Description'], [
    ['Review', '5', 'Rapid reading of syllables and words from previous sessions'],
    ['Explicit teaching', '7', 'The teacher models blending the new syllables and words (“I do”)'],
    ['Guided practice', '8', 'Learners blend and read with prompts and immediate corrective feedback (“We do”)'],
    ['Independent practice', '7', 'Learners read word lists, sort words, or play syllable games with a partner (“You do”)'],
    ['Check and closure', '3', 'Each learner reads five words aloud; results are recorded in the implementation log'],
  ], { aligns: [L, C, L], size: 20 }),

  h.h2('Research Instrument'),
  h.runIn('Letter-Sound Screening.', 'A one-page screening sheet with the 20 letters of the Abakada (a, b, k, d, e, g, h, i, l, m, n, ng, o, p, r, s, t, u, w, y) will be used to confirm that each learner can give at least 15 letter sounds. It is used only for selecting respondents and is not part of the pre-test or post-test.'),
  h.runIn('Filipino Word Recognition Test (FWRT).', 'This researcher-made test will measure word recognition before and after the intervention. It has two equivalent forms, Form A for the pre-test and Form B for the post-test, each with 45 Filipino words: 15 two-syllable words with open syllables, 15 two-syllable words with a closed final syllable, and 15 three-syllable words. The words are common, concrete words appropriate for Grade 2 learners and aligned with the Grade 2 Filipino competencies of the MATATAG Curriculum (Department of Education, 2024b), and none of them is taught in the RIM. Table 4 presents the items.'),
  ...h.ntable('Items of the Filipino Word Recognition Test', [28, 36, 36], ['Syllable Pattern (15 items each)', 'Form A (Pre-test)', 'Form B (Post-test)'], itemRows, { aligns: [L, L, L], size: 18, vTop: true }),
  h.p('The test is administered individually. The words are printed in large type on cards, one pattern per card, and the learner reads each word aloud. A word is scored 1 if it is read correctly within three seconds and 0 if it is misread, skipped, or read correctly only after more than three seconds. Scores are recorded separately for each pattern (maximum of 15 each) and summed for overall word recognition (maximum of 45). Testing stops within a pattern if the learner misses five words in a row. Each administration takes about 10 minutes and is audio-recorded with parental consent.'),
  h.runIn('Implementation Log.', 'The researcher will record the date, attendance, module, activities, and check results of every session. The log is used to document that the intervention was delivered as planned and to apply the attendance criterion; it is not used to answer a separate research objective.'),
  h.runIn('Validation of the Instrument.', 'The FWRT will be validated in three stages. First, a panel of six experts, composed of a master teacher in reading, the school reading coordinator, two Filipino teachers, a school head or education program supervisor, and a research expert, will rate the relevance of each item to its syllable pattern and grade level on a four-point scale. Items with an item-level content validity index (I-CVI) below .78 will be revised or replaced, and a scale-level average (S-CVI/Ave) of .90 or higher will indicate excellent content validity (Lynn, 1986; Polit & Beck, 2006). Second, both forms will be pilot-tested with 20 to 30 Grade 2 learners from a comparable class or school who are not part of the study. Reliability will be estimated for each pattern and for the whole test using the Kuder–Richardson Formula 20 (Kuder & Richardson, 1937), with .70 or higher considered acceptable, and the forms will be considered equivalent if their scores are strongly correlated and do not differ significantly. Third, a second trained rater, unaware of whether a recording came from the pre-test or the post-test, will independently score at least 20 percent of the recordings; an agreement of at least 90 percent will be required.'),

  h.h2('Data Gathering Procedures'),
  h.p('Data gathering will take about ten weeks within the third quarter of School Year 2026–2027, as summarized in Table 5.'),
  ...h.ntable('Timeline of Data Gathering', [18, 54, 28], ['Week', 'Activity', 'Output'], [
    ['Before Week 1', 'Approval of the proposal; permission from the Schools Division Superintendent and the school principal; parent orientation and informed consent', 'Approved requests; signed consent forms'],
    ['1–2', 'Content validation and pilot testing of the FWRT', 'Validated and reliable test'],
    ['3', 'Letter-sound screening; pre-test (Form A)', 'List of respondents; baseline scores'],
    ['4–9', 'Six-week intervention using the Syllable-Based RIM (24 sessions)', 'Implementation log'],
    ['10', 'Post-test (Form B); second-rater scoring', 'Post-test scores; inter-rater agreement'],
    ['After Week 10', 'Encoding, analysis, and reporting of data', 'Research report'],
  ], { aligns: [C, L, L], size: 20 }),
  h.runIn('Securing Permission.', 'After the proposal is approved by the Graduate School of Bicol College, the researcher will request permission from the Schools Division Superintendent, through the Public Schools District Supervisor, in accordance with the DepEd research management guidelines (Department of Education, 2017), and will coordinate the schedule with the principal of Albay Central School.'),
  h.runIn('Informed Consent.', 'An orientation will be held for the parents or guardians of the identified learners. Written consent will be obtained from the parents, and each learner’s verbal assent will be sought in simple Filipino or Bikol.'),
  h.runIn('Screening and Pre-test.', 'In Week 3, the learners classified at the frustration level will take the letter-sound screening. Those who give at least 15 letter sounds and meet the other criteria will take Form A of the FWRT individually in a quiet room, following standardized directions.'),
  h.runIn('Intervention.', 'From Weeks 4 to 9, the learners will use the Syllable-Based RIM in 24 small-group sessions following the routine in Table 3. Attendance and session results will be recorded in the implementation log.'),
  h.runIn('Post-test and Data Processing.', 'In Week 10, Form B will be administered under the same conditions as the pre-test, and the second rater will score the selected recordings. Scores will be encoded in a spreadsheet, verified through double entry, and analyzed as described in the data analysis plan. Learners who still need support after the study will continue to receive reading assistance.'),

  h.h2('Respondents of the Study'),
  h.p('The respondents will be the Grade 2 frustration-level readers of Albay Central School in School Year 2026–2027 who meet the following inclusion criteria: (a) classified as reading at the frustration level in the beginning-of-the-year reading assessment administered by the school; (b) able to give at least 15 of the 20 letter sounds in the screening; (c) with the written consent of their parents or guardians and their own assent; and (d) expected to remain enrolled for the duration of the study.'),
  h.p('Learners will be excluded if they (a) give fewer than 15 letter sounds, since their primary need is letter-sound instruction rather than blending; (b) have a diagnosed condition, such as an uncorrected visual or hearing impairment, that requires specialized intervention, in which case they will be referred for appropriate support; or (c) attend fewer than 80 percent of the sessions (fewer than 20 of 24), in which case their scores will be excluded from the analysis although they will continue to receive support.'),

  h.h2('Sampling Technique'),
  h.p('The study will use purposive sampling, a non-probability technique in which participants are selected because they have the characteristics the study requires (Etikan et al., 2016). Because the population is small and specifically defined, the study will use complete enumeration: all Grade 2 learners of Albay Central School who meet the inclusion criteria will be included. The sample is therefore the entire target population in the school, which removes sampling error within the school. The exact number of respondents will be known after the screening and the securing of consent.'),

  h.h2('Study Site'),
  h.p('The study will be conducted at Albay Central School, a public elementary school under the Department of Education in the Province of Albay, Bicol Region. The school is an appropriate site for three reasons. First, its learners mostly speak Bikol at home and are learning to read in Filipino, which makes the bridge from letter sounds to Filipino word reading an immediate instructional concern. Second, the school’s beginning-of-the-year reading assessment has identified Grade 2 learners reading at the frustration level, establishing a clear need. Third, the school implements remedial reading and Catch-Up Fridays, which provide regular time for the intervention, and it is the researcher’s own workplace, which allows daily access to the learners and consistent delivery of all 24 sessions. Conducting the study in the researcher’s own school is consistent with the DepEd research management guidelines, which encourage teachers to undertake research that improves teaching and learning in their schools (Department of Education, 2017).'),

  h.h2('Data Analysis Plan'),
  h.p('Data will be encoded in Microsoft Excel and analyzed using statistical software such as SPSS or jamovi, with the level of significance set at .05.'),
  h.runIn('Objectives 1 and 2.', 'The mean, standard deviation, frequency, and percentage will be used to describe the learners’ word recognition in each syllable pattern and overall, before and after the intervention. Scores will be converted to percentages and interpreted using Table 6.'),
  ...h.ntable('Scale for Interpreting Word Recognition Scores', [22, 30, 48], ['Percentage of Words Read Correctly', 'Word Recognition Level', 'Description'], [
    ['90–100', 'Proficient', 'Recognizes words of the pattern accurately and automatically'],
    ['75–89', 'Approaching Proficiency', 'Recognizes most words of the pattern, with occasional errors or delays'],
    ['50–74', 'Developing', 'Recognizes some words of the pattern; blending is inconsistent'],
    ['Below 50', 'Beginning', 'Recognizes few words of the pattern; needs intensive support'],
  ], { aligns: [C, L, L], size: 20 }),
  h.runIn('Objective 3.', 'The normality of the differences between the pre-test and post-test scores will be examined using the Shapiro–Wilk test, which is suited to small samples (Shapiro & Wilk, 1965). If the differences are normally distributed, the paired-samples t-test will be used; otherwise, the Wilcoxon signed-rank test (Wilcoxon, 1945) will be applied. The test will be run for each syllable pattern and for overall word recognition, and the null hypothesis will be rejected if p < .05. The 95 percent confidence interval of the mean difference will be reported, and the magnitude of the change will be expressed as Cohen’s d (or r for the Wilcoxon test), interpreted using Cohen’s (1988) benchmarks of small (0.20), medium (0.50), and large (0.80) effects.'),

  h.h2('Ethical Considerations'),
  h.p('The study will observe the principles of respect for persons, beneficence, and justice (National Commission for the Protection of Human Subjects of Biomedical and Behavioral Research, 1979). Parents or guardians will give written informed consent, and each learner will give verbal assent; participation is voluntary, and a learner may withdraw at any time without any effect on grades or on access to regular reading support. Sessions will be conducted in a safe and supportive manner in accordance with the DepEd Child Protection Policy (Department of Education, 2012) and will not take time from regular classes. All eligible learners will receive the intervention, and those who still need help after the study will continue to receive support. In compliance with the Data Privacy Act of 2012 (Republic Act No. 10173, 2012), learners’ names will be replaced with codes, recordings will be used only for scoring and verification, and all data will be kept secure and reported only in aggregate form.'),
];

// ---------- references ----------
const ref = (pieces) => new Paragraph({
  alignment: AlignmentType.LEFT, indent: { left: 720, hanging: 720 }, spacing: { after: 120, line: 240 },
  children: pieces.map(([t, o = {}]) => new TextRun({ text: t, ...o })),
});
const book = (a, y, t, rest) => ref([[`${a} (${y}). `], [t, I], [rest]]);
const art = (a, y, t, j, vol, pages) => ref([[`${a} (${y}). ${t} `], [`${j}, ${vol.split('(')[0]}`, I], [`(${vol.split('(')[1]}, ${pages}.`]]);
const DE = 'Department of Education.';
const refs = [
  section('REFERENCES', true),
  book('Campbell, D. T., & Stanley, J. C.', 1963, 'Experimental and quasi-experimental designs for research', '. Rand McNally.'),
  art('Cheung, A. C. K., & Slavin, R. E.', 2016, 'How methodological features affect effect sizes in education.', 'Educational Researcher', '45(5)', '283–292'),
  book('Cohen, J.', 1988, 'Statistical power analysis for the behavioral sciences', ' (2nd ed.). Lawrence Erlbaum Associates.'),
  book(DE, 2012, 'DepEd Order No. 40, s. 2012: DepEd child protection policy', '. DepEd.'),
  book(DE, 2016, 'DepEd Order No. 35, s. 2016: The Learning Action Cell as a K to 12 Basic Education Program school-based continuing professional development strategy for the improvement of teaching and learning', '. DepEd.'),
  book(DE, 2017, 'DepEd Order No. 16, s. 2017: Research management guidelines', '. DepEd.'),
  book(DE, 2018, 'DepEd Order No. 14, s. 2018: Policy guidelines on the administration of the revised Philippine Informal Reading Inventory', '. DepEd.'),
  book(DE, 2019, 'DepEd Memorandum No. 173, s. 2019: Hamon: Bawat Bata Bumabasa (3Bs Initiative)', '. DepEd.'),
  book(DE, 2023, 'DepEd Order No. 13, s. 2023: Policy guidelines on the implementation of the National Learning Recovery Program', '. DepEd.'),
  book(DE, '2024a', 'DepEd Memorandum No. 001, s. 2024: Implementation of Catch-Up Fridays', '. DepEd.'),
  book(DE, '2024b', 'DepEd Order No. 10, s. 2024: Policy guidelines on the implementation of the MATATAG Curriculum', '. DepEd.'),
  art('Ehri, L. C.', 2005, 'Learning to read words: Theory, findings, and issues.', 'Scientific Studies of Reading', '9(2)', '167–188'),
  art('Etikan, I., Musa, S. A., & Alkassim, R. S.', 2016, 'Comparison of convenience sampling and purposive sampling.', 'American Journal of Theoretical and Applied Statistics', '5(1)', '1–4'),
  book('Fraenkel, J. R., Wallen, N. E., & Hyun, H. H.', 2012, 'How to design and evaluate research in education', ' (8th ed.). McGraw-Hill.'),
  art('Gough, P. B., & Tunmer, W. E.', 1986, 'Decoding, reading, and reading disability.', 'Remedial and Special Education', '7(1)', '6–10'),
  art('Hoover, W. A., & Gough, P. B.', 1990, 'The simple view of reading.', 'Reading and Writing', '2(2)', '127–160'),
  art('Juel, C.', 1988, 'Learning to read and write: A longitudinal study of 54 children from first through fourth grades.', 'Journal of Educational Psychology', '80(4)', '437–447'),
  art('Kuder, G. F., & Richardson, M. W.', 1937, 'The theory of the estimation of test reliability.', 'Psychometrika', '2(3)', '151–160'),
  art('LaBerge, D., & Samuels, S. J.', 1974, 'Toward a theory of automatic information processing in reading.', 'Cognitive Psychology', '6(2)', '293–323'),
  art('Lynn, M. R.', 1986, 'Determination and quantification of content validity.', 'Nursing Research', '35(6)', '382–385'),
  art('Mesmer, H. A. E.', 2001, 'Decodable text: A review of what we know.', 'Reading Research and Instruction', '40(2)', '121–141'),
  book('National Commission for the Protection of Human Subjects of Biomedical and Behavioral Research.', 1979, 'The Belmont report: Ethical principles and guidelines for the protection of human subjects of research', '. U.S. Department of Health, Education, and Welfare.'),
  book('National Reading Panel.', 2000, 'Teaching children to read: An evidence-based assessment of the scientific research literature on reading and its implications for reading instruction', '. National Institute of Child Health and Human Development.'),
  book('OECD.', 2019, 'PISA 2018 results (Volume I): What students know and can do', '. OECD Publishing.'),
  book('OECD.', 2023, 'PISA 2022 results (Volume I): The state of learning and equity in education', '. OECD Publishing.'),
  art('Polit, D. F., & Beck, C. T.', 2006, 'The content validity index: Are you sure you know what’s being reported? Critique and recommendations.', 'Research in Nursing & Health', '29(5)', '489–497'),
  book('Republic Act No. 10173.', 2012, 'Data Privacy Act of 2012', '. Congress of the Philippines.'),
  book('Republic Act No. 10533.', 2013, 'Enhanced Basic Education Act of 2013', '. Congress of the Philippines.'),
  book('Republic Act No. 12028.', 2024, 'Academic Recovery and Accessible Learning (ARAL) Program Act', '. Congress of the Philippines.'),
  art('Seymour, P. H. K., Aro, M., & Erskine, J. M.', 2003, 'Foundation literacy acquisition in European orthographies.', 'British Journal of Psychology', '94(2)', '143–174'),
  art('Shapiro, S. S., & Wilk, M. B.', 1965, 'An analysis of variance test for normality (complete samples).', 'Biometrika', '52(3–4)', '591–611'),
  art('Stanovich, K. E.', 1986, 'Matthew effects in reading: Some consequences of individual differences in the acquisition of literacy.', 'Reading Research Quarterly', '21(4)', '360–407'),
  book('Tomlinson, B. (Ed.).', 2011, 'Materials development in language teaching', ' (2nd ed.). Cambridge University Press.'),
  art('Torgesen, J. K.', 2004, 'Avoiding the devastating downward spiral: The evidence that early intervention prevents reading failure.', 'American Educator', '28(3)', '6–19'),
  book('UNICEF & SEAMEO.', 2020, 'SEA-PLM 2019 main regional report: Children’s learning in 6 Southeast Asian countries', '. UNICEF & SEAMEO–SEA-PLM Secretariat.'),
  book('Vygotsky, L. S.', 1978, 'Mind in society: The development of higher psychological processes', '. Harvard University Press.'),
  art('Wanzek, J., & Vaughn, S.', 2007, 'Research-based implications from extensive early reading interventions.', 'School Psychology Review', '36(4)', '541–561'),
  art('Wilcoxon, F.', 1945, 'Individual comparisons by ranking methods.', 'Biometrics Bulletin', '1(6)', '80–83'),
  art('Wood, D., Bruner, J. S., & Ross, G.', 1976, 'The role of tutoring in problem solving.', 'Journal of Child Psychology and Psychiatry', '17(2)', '89–100'),
  book('World Bank.', 2022, 'The state of global learning poverty: 2022 update', '. World Bank.'),
];

const doc = new Document({
  creator: 'Irene A. Loria',
  title: 'Introduction and Methodology',
  styles: { default: { document: { run: { font: 'Arial', size: 24 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 2160 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] }) },
    children: [...body, ...refs],
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(process.argv[2], buf); console.log('written', process.argv[2], '| tables', h.state.tables.length, '| figures', h.state.figures.length); });
