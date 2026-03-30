/**
 * Tests for grade utility functions.
 */

import { getGrade, getBarColor } from '../utils/gradeUtils';

describe('getGrade', () => {
  test('returns A for scores >= 90', () => {
    expect(getGrade(90)).toBe('A');
    expect(getGrade(100)).toBe('A');
    expect(getGrade(95)).toBe('A');
  });

  test('returns B for scores >= 80 and < 90', () => {
    expect(getGrade(80)).toBe('B');
    expect(getGrade(89)).toBe('B');
  });

  test('returns C for scores >= 70 and < 80', () => {
    expect(getGrade(70)).toBe('C');
    expect(getGrade(79)).toBe('C');
  });

  test('returns D for scores >= 60 and < 70', () => {
    expect(getGrade(60)).toBe('D');
    expect(getGrade(69)).toBe('D');
  });

  test('returns F for scores < 60', () => {
    expect(getGrade(59)).toBe('F');
    expect(getGrade(0)).toBe('F');
  });
});

describe('getBarColor', () => {
  test('returns green for A-range scores', () => {
    expect(getBarColor(90)).toBe('bg-green-500');
  });

  test('returns blue for B-range scores', () => {
    expect(getBarColor(80)).toBe('bg-blue-500');
  });

  test('returns yellow for C-range scores', () => {
    expect(getBarColor(70)).toBe('bg-yellow-500');
  });

  test('returns orange for D-range scores', () => {
    expect(getBarColor(60)).toBe('bg-orange-500');
  });

  test('returns red for F-range scores', () => {
    expect(getBarColor(50)).toBe('bg-red-500');
  });
});
