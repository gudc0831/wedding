import fs from "node:fs";

const guides = [
  { file: "czech_honeymoon_guide.html", expected: 46 },
  { file: "switzerland_honeymoon_guide.html", expected: 39 },
];

const forbidden = /엑셀|Excel|스프레드시트|가져왔/i;
const errors = [];
const summaries = [];

for (const guide of guides) {
  const html = fs.readFileSync(guide.file, "utf8");
  const tags = html.match(/<div\b(?=[^>]*\bclass="[^"]*\bcalendar-event\b[^"]*")[^>]*>/g) || [];
  let withDetail = 0;
  let invalidSegments = 0;

  tags.forEach((tag, index) => {
    const match = tag.match(/\bdata-detail="([^"]*)"/);
    if (!match) {
      errors.push(`${guide.file}: calendar event ${index + 1} is missing data-detail`);
      return;
    }
    const segments = match[1].split("|").map((value) => value.trim()).filter(Boolean);
    if (segments.length < 2) {
      invalidSegments += 1;
      errors.push(`${guide.file}: calendar event ${index + 1} has ${segments.length} detail segment(s)`);
      return;
    }
    withDetail += 1;
  });

  if (tags.length !== guide.expected) {
    errors.push(`${guide.file}: expected ${guide.expected} events, found ${tags.length}`);
  }
  if (forbidden.test(html)) {
    errors.push(`${guide.file}: forbidden source wording found`);
  }

  summaries.push({
    file: guide.file,
    events: tags.length,
    withDetail,
    missingDetail: tags.length - withDetail,
    invalidSegments,
  });
}

console.log(JSON.stringify(summaries, null, 2));
if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
console.log("SCHEDULE_DETAIL_VALIDATION_PASS");
