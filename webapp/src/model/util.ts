export function get(object: any, keyPath: string) {
  return keyPath.split('.').reduce((previous, current) => previous && previous[current], object);
}

/**
 * Summarise a dictionary of values, where the keys are the names of the
 * platform that value was found on.
 *
 * - If all the values are the same, return that value.
 * - If there is a tie, return a list of all the values.
 * - If there is a majority, return the majority value, with the rest in
 *   brackets.
 */
export function summariseValues(valueDict: {[key: string]: string}): string {
    const keys = Object.keys(valueDict);
    const valueCounts: {value: string, keys: string[]}[] = []

    for (const key of keys) {
        const value = valueDict[key]
        let counter = valueCounts.find(c => c.value === value)
        if (!counter) {
            counter = {value, keys: []}
            valueCounts.push(counter)
        }
        counter.keys.push(key)
    }

    valueCounts.sort((a, b) => b.keys.length - a.keys.length)

    if (valueCounts.length === 0) {
        return '';
    } else if (valueCounts.length == 1) {
        return valueCounts[0].value;
    } else {
        if (valueCounts[0].keys.length > valueCounts[1].keys.length) {
            // we have the majority in one group, so just separate out the rest.
            const rest = valueCounts.slice(1).map(c => `${c.value} on ${formatList(c.keys)}`).join(', ')
            return `${valueCounts[0].value || 'None'} (${rest})`
        } else {
            // we have a tie, so just list all the values.
            return valueCounts.map(c => `${c.value} on ${formatList(c.keys)}`).join(', ')
        }
    }
}

export function formatList(list: string[]): string {
    if (list.length === 0) {
        return '';
    } else if (list.length === 1) {
        return list[0];
    } else {
        list = list.slice();
        const last = list.pop();
        return `${list.join(', ')} and ${last}`;
    }
}

export function entries<T>(object: {[key: string]: T}): [string, T][] {
    return Object.keys(object).map(key => [key, object[key]]);
}

export function reversed<T>(iterable: Iterable<T>): Array<T> {
    const result = Array.from(iterable)
    result.reverse()
    return result
}

export function regexExtract(text: string|null, regex: RegExp): string|null {
    const match = text?.match(regex)
    if (!match) return null
    return match[1]
}

export function dateFromImageTag(tag: string) {
    // tag looks like 2023-04-09-db9a92f
    console.log(tag)
    const [year, month, day] = tag.split(/[-\.]/g).slice(0, 3).map(s => parseInt(s))
    console.log(year, month, day)
    return new Date(year, month - 1, day)
}

export function commitFromImageTag(tag: string) {
    // tag looks like 2023-04-09-db9a92f
    return tag.split('-')[3]
}

export function timeAgo(date: Date): string {
  const now = new Date();
  const msPerDay = 24 * 60 * 60 * 1000;
  const daysAgo = Math.floor((now.getTime() - date.getTime()) / msPerDay);

  if (daysAgo === 0) {
    return "today";
  } else if (daysAgo === 1) {
    return "yesterday";
  } else if (daysAgo < 50) {
    return `${daysAgo} days ago`;
  } else if (daysAgo < 700) {
    return `${Math.floor(daysAgo / 30)} months ago`;
  } else {
    return `${Math.floor(daysAgo / 365)} years ago`;
  }
}

export function compareArchs(a: string, b: string) {
    const order = ['x86_64', 'i686', 'aarch64', 'ppc64le', 's390x']
    const aPos = order.indexOf(a)
    const bPos = order.indexOf(b)

    if (aPos === -1 && bPos === -1) {
        return a.localeCompare(b)
    }
    if (aPos === -1) {
        return 1
    }
    if (bPos === -1) {
        return -1
    }
    return aPos - bPos
}

export function unique<T>(array: T[]): T[] {
    return Array.from(new Set(array))
}

