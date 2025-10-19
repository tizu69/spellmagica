As many of the hexcasters may have noticed, type syntax in documentation is all over the place. This proposal is to standardize the syntax for types within Hexcasting documentation, for both human and machine readers.

The syntax section of this document contains some collapsed examples. These are represented as JSON. In reality, these would be represented as the Hexcasting equivalent of the JSON, like an array of patterns instead of a string.

**This is not a final document.** It is an RFC - a request for comments. Tell me what you think, get updating.

## Definitions

- **type** A type is a representation of a type of iota, like number or string.
- **stack** The stack is the list of iotas present in memory.
- **iota** An iota is a single value in the stack.
- **pattern** A "function".
- **input** The input is the top of the stack before the pattern is run.
- **output** The output is the top of the stack after the pattern is run.

## Usage

Like the old "syntax", the last item in the array is the "uppermost" stack item, that is to say, the iota of the top of the stack.

This proposal proposes a JSON-based tree syntax for types. Depending on the implementation in Hexcasting, this may be another format, like XML, a Builder pattern in Code, or something else with similar structure. Tools that export documentation to JSON (like HexBug) should use `inputs` and `outputs` keys to indicate input and output types, both of which are an array.

As such, any type root should be an array. If no input or output types are given, this proposal suggests an empty array, `[]`, although a `null` may also be feasible. This should not be mixed, so choose globally.

## Syntax

The following documentation specifies a single iotan type. The most basic type is an **any type**. As the name implies, this can represent any iota. It is written as an empty string.

```json
""
```

<details>
<summary>Tests</summary>

### Valid 

```json
123.45
```

```json
"aadadaaw"
```

```json
[[[[1, 2]]]]
```
</details>

An **iota type** is a type that represents a specific iota. It is written as an identifier, such as `hexcasting:number` or `moreiotas:string`. The identifier should be the mod id, followed by a colon, followed by the type name. This spec enforces the name (after the `:`) to be lowercase letters only. This allows it to be used as a display name in the UI (for example).

```json
"hexcasting:number"
```

<details>
<summary>Tests</summary>

### Valid 

```json
123.45
```

### Invalid

```json
"aadadaaw"
```
</details>

A **tuple type** is a type that represents a tuple of iotas (an array with a fixed length and position of types). It is written as a `tuple` key, followed by an array of types.

```json
{ "tuple": ["hexcasting:number", "hexcasting:number"] }
```

<details>
<summary>Tests</summary>

### Valid 

```json
[123.45, 123.45]
```

### Invalid

```json
[123.45, 123.45, 123.45]
```

```json
[123.45]
```

```json
123.45
```
</details>

A **union type** is a type that represents a union of types (one of a set of iotas). It is written as an `oneof` key, followed by an array of types.

```json
{ "oneof": ["hexcasting:number", "hexcasting:player"] }
```

<details>
<summary>Tests</summary>

### Valid 

```json
123.45
```

```json
<Petrak>
```

### Invalid

```json
[123.45, 123.45]
```
</details>

An **array type** is a type that represents an array of iotas. It is written as an `array` key, followed by a type.

```json
{ "array": "hexcasting:number" }
```

<details>
<summary>Tests</summary>

### Valid 

```json
[123.45, 123.45]
```

```json
[123.45, 123.45, 123.45, 123.45, 123.45, 123.45, 123.45, 123.45, 123.45, 123.45]
```

### Invalid

```json
123.45
```

```json
["wqw"]
```
</details>

An **optional type** is a type that represents an optional iota. It is written as an `optional` key, followed by a type. Optional types may be empty if the stack is not long enough.

If not at the top of the stack, this type implies that if the type does not match, the iota is ignored and kept. If at the top of the stack, this type will fail if the type does not match the optional type, or the type before.

This type should **not** be used - prefer using a `{ "oneof": [type, "hexcasting:null"] }` instead. It exists because mods have already made use of this behaviour.

```json
{ "optional": "hexcasting:number" }
```

<details>
<summary>Tests</summary>

### Valid 

```json
123.45
```

```json
```

```json
// This value gets ignored and not pulled from the stack.
[123.45, 123.45]
```
</details>

A **stack exhaust type** is a type that represents an unspecified number of iotas. It is written as a `"..."` key. Only one is allowed in a single input or output, and the number of other types before/after define how many iotas are stripped from this type, so `["hexcasting:number", "...", "hexcasting:number"]`
implies, that the uppermost type is `hexcasting:number`, the "lowermost" type is also `hexcasting:number`, and the remaining types in-between are not explicitly type-defined. This type should generally be avoided, as it makes it difficult to automatically infer stack size without testing, but if required, it may be used.

This is a black box - it does not define the length of taken iotas. It should **not** be used unless you know what you're doing and the description of the pattern should define how many iotas are taken. It exists because mods have already made use of this behaviour, and for stack manipulation, it is somewhat required. `[0, 0, 0, 0, 0]` may end up as `[0, 0]` or `[0, 0, 0, 0]` if not documented properly.

```json
"..."
```

## Metatypes

Not all types are "real". For example, a `hexcasting:vector` is not really a real type, but moreso, a `tuple` of three `hexcasting:number`s. These metatypes should be defined in HexBug in a `metatypes` key. How this works in-game is unspecified, as this is mostly for documentation and machine parsing purposes.

```json
{
    "metatypes": {
        "hexcasting:vector": {
            "tuple": ["hexcasting:number", "hexcasting:number", "hexcasting:number"]
        }
    }
}
```

## Limitations

- No generics are supported.
- No recursion is supported.
- Clamped types, like `0-24` or `int >= 0` are not supported.
- You tell me!

## Examples

These examples are from the registry.json that HexBug provides.

```json
{
    "description": "Copy the top two iotas of the stack. [0, 1] becomes [0, 1, 0, 1].",
    // "inputs": "any, any",
    "inputs": ["", ""],
    // "outputs": "any, any, any, any",
    "outputs": ["", "", "", ""],
    "book_url": "https://hexcasting.hexxy.media/v/0.11.2/1.0/en_us#patterns/stackmanip@hexcasting:2dup",
    "mod_id": "hexcasting"
}
```

```json
{
    "description": "Takes the intersection of two sets.",
    // "inputs": "(num, num)|(list, list)",
    "inputs": [{
        "oneof": [
            { "tuple": ["hexcasting:number", "hexcasting:number"] },
            { "tuple": [{ "array": "" }, { "array": "" }] }
        ]
    }],
    // "outputs": "num|list",
    "outputs": [{
        "oneof": [
            "hexcasting:number",
            { "array": "" }
        ]
    }],
    "book_url": "https://hexcasting.hexxy.media/v/0.11.2/1.0/en_us#patterns/sets@hexcasting:and",
    "mod_id": "hexcasting"
}
```

```json
{
	"description": "Removes a string and a bool or null. If it was true, return the string in upper case. If false, lowercase. If null, toggle each character's case.",
	// "inputs": "str, bool | null",
    "inputs": ["hexcasting:string", { "oneof": ["hexcasting:boolean", "hexcasting:null"] }],
	// "outputs": "str",
    "outputs": ["hexcasting:string"],
	"book_url": "https://moreiotas.hexxy.media/v/0.1.1/1.0/en_us#patterns/strings@moreiotas:string/case",
	"mod_id": "moreiotas"
}
```