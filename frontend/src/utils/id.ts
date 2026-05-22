let counter = 0;

export function genId(): string {
  counter += 1;
  return `${Date.now()}-${counter}`;
}
