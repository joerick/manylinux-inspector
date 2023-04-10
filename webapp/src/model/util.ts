
// export const reportsData = reportsDataUntyped as {
//     reports: ReportData[],
//     latest: {
//         metadata: {generated_at: number},
//         data: {[repository: string]: string},
//     },
// }

// interface ReportData {
//     metadata: {
//         image: string,
//         generated_at: number
//     },
//     data: any,
// }

// class ImageReport {
//     nameInfo: ImageNameParts;
//     data: any;

//     constructor(
//         data: ReportData,
//     ) {
//         this.nameInfo = parseImageName(data.metadata.image);
//         this.data = data.data
//     }

//     getField(keypath: string): string {
//         return get(this.data, keypath)?.toString() ?? '';
//     }
// }

// class ManylinuxVersion {
//     archs: {[arch: string]: ImageReport} = {};

//     static withName

//     constructor(
//         readonly domain: string,
//         readonly org: string,
//         readonly name: string,
//         readonly tag: string,
//     ) {}

//     get id(): string {
//         return `${this.domain}/${this.org}/${this.name}:${this.tag}`;
//     }

//     addReport(report: ImageReport) {
//         this.archs[report.nameInfo.arch] = report;
//     }

//     getFieldKeypaths(): string[] {
//         const keypaths = new Set<string>();


//     getField(keypath: string): string {
//         const valueDict: {[key: string]: string} = {}
//         for (const arch of Object.keys(this.archs)) {
//             valueDict[arch] = this.archs[arch].getField(keypath)
//         }
//         return summariseValues(valueDict)
//     }

//     getKeypaths(): string[] {
//         const keypaths = new Set<string>();
//         for (const arch of Object.keys(this.archs)) {
//             for (const keypath of listKeypaths(this.archs[arch].data)) {
//                 keypaths.add(keypath);
//             }
//         }
//         return Array.from(keypaths);
//     }
// }

// interface ImageNameParts {
//     domain: string,
//     org: string,
//     name: string,
//     arch: string,
//     tag: string,
// }
// function parseImageName(imageName: string): ImageNameParts {
//     const regex = /^(?<domain>.*)\/(?<org>.*)\/(?<name>[a-z]*(?:\d|\d\d\d\d|(?:_\d+)+))_(?<arch>.*):(?<tag>.*)$/i;
//     const match = imageName.match(regex);
//     if (!match) {
//         throw new Error(`Invalid image name: ${imageName}`);
//     }
//     return {
//         domain: match[1],
//         org: match[2],
//         name: match[3],
//         arch: match[4],
//         tag: match[5],
//     };
// }

// export function getManylinuxVersions(): ManylinuxVersion[] {
//     const reports = reportsData.reports.map(d => new ImageReport(d));
//     const versions: ManylinuxVersion[] = []

//     for (const report of reports) {
//         const {domain, org, name, tag} = report.nameInfo;
//         let version = versions.find(v => v.domain === domain && v.org === org && v.name === name && v.tag === tag);
//         if (!version) {
//             version = new ManylinuxVersion(domain, org, name, tag);
//             versions.push(version);
//         }
//         version.addReport(report);
//     }
//     return versions;
// }



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

function formatList(list: string[]): string {
    if (list.length === 0) {
        return '';
    } else if (list.length === 1) {
        return list[0];
    } else {
        const last = list.pop();
        return `${list.join(', ')} and ${last}`;
    }
}

function listKeypaths(object: any): string[] {
  const keypaths = [];
  for (const key in object) {
    if (object.hasOwnProperty(key)) {
      if (typeof object[key] === 'object') {
        const subkeypaths = listKeypaths(object[key]);
        for (const subkeypath of subkeypaths) {
          keypaths.push(key + '.' + subkeypath);
        }
      } else {
        keypaths.push(key);
      }
    }
  }
  return keypaths;
}

interface Object {
    __cachedProperty?: {
        [key: string]: any;
    }
}
export function cachedProperty<This extends Object, Return>(
    target: (this: This) => Return,
    context: ClassGetterDecoratorContext<This, (this: This) => Return>
) {
    const methodName = String(context.name);

    function replacementMethod(this: This): Return {
        if (!this.__cachedProperty) {
            this.__cachedProperty = {};
        }
        if (methodName in this.__cachedProperty) {
            return this.__cachedProperty[methodName];
        }
        const result = target.call(this);
        this.__cachedProperty[methodName] = result;
        return result;
    }

    return replacementMethod;
}

export function entries<T>(object: {[key: string]: T}): [string, T][] {
    return Object.keys(object).map(key => [key, object[key]]);
}

export function reversed<T>(iterable: Iterable<T>): Array<T> {
    const result = Array.from(iterable)
    result.reverse()
    return result
}
