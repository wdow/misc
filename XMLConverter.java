/*
*   Class XMLConverter
*   Will Dower (william.dower@nist.gov)
*   A script to convert old constraint files to the new structure.
*   Takes the old constraint XML as input, generates a new XML file as output.
*   Date: 06/06/2016
*/

/*
*   Current issue(s):
*   - Can't swtich contexts from a segment to another segment in the middle
*   of a constraint
*
*
*/

// For using StAX to read in the old XML constraint file
import java.io.*;
import java.util.Iterator;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;
import javax.xml.stream.events.Attribute;
import javax.xml.stream.events.Characters;
import javax.xml.stream.events.EndElement;
import javax.xml.stream.events.StartElement;
import javax.xml.stream.events.XMLEvent;
import javax.xml.namespace.QName;

// For using StAX to write the new XML constraint file
import java.io.FileWriter;
import javax.xml.stream.XMLOutputFactory;
import javax.xml.stream.XMLStreamWriter;

// for pretty printing
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import org.w3c.dom.Document;
import org.xml.sax.SAXException;
import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.OutputKeys;

// Main
public class XMLConverter {

    public static void main(String[] args) {

        String inputFile;
        String outputFile;

        // flags to track if the current tags are in an <IfThenElse> tag
        boolean ifFlag = false;
        boolean thenFlag = false;

        // only allow reading in plain text if it within a set of <Value> tags
        boolean allowCharReading = false;

        // a string to store the 'field[component].subcomponent' address of the
        // value to be tested
        String path = "";

        // the name of the message segment
        String name = "";

        // the data to be checked
        String value = "";
        String valueDataType = "";
        String valueDescriptor = "";

        //check for valid args
        if(args.length == 0) {
            System.out.print("Usage: $ java XMLConverter [input file]");
            System.out.println(" [output file]");
            //inputFile = "C:\\Users\\wdd\\Desktop\\Summer2016\\Albert_Hon_HO2009001.xml";
            //outputFile = "C:\\Users\\wdd\\Desktop\\Summer2016\\output.xml";

        } else {
            inputFile = args[1];
            outputFile = args[2];
        }


        XMLInputFactory xmlin;
        XMLOutputFactory xmlout;

        XMLEventReader eventReader;
        XMLStreamWriter writer;

        XMLEvent event;

        String elementName;
        Iterator<Attribute> attributes;

        int idCounter = 1;

        try {

            // set up the input factory
            xmlin = XMLInputFactory.newInstance();
            eventReader = xmlin.createXMLEventReader(new FileReader(inputFile));

            xmlout = XMLOutputFactory.newInstance();
            writer = xmlout.createXMLStreamWriter(new FileWriter(outputFile));

            //writer.writeStartDocument("UTF-8", "1.0");

            writer.writeStartElement("Segment"); // <Segment>
            writer.writeStartElement("Constraints"); // <Constraints>
            writer.writeEmptyElement("Datatype"); // <Datatype/>

            // start crawling through inputFile
            while(eventReader.hasNext()) {
                //System.out.println("Event!");
                event = eventReader.nextEvent();

                switch(event.getEventType()) {

                    case XMLStreamConstants.START_DOCUMENT:

                        break;


                    case XMLStreamConstants.START_ELEMENT:

                        StartElement startElement = event.asStartElement();

                        elementName = startElement.getName().getLocalPart();

                        attributes = startElement.getAttributes();

                        switch(elementName) {

                            case "Segment":
                                /*System.out.println("\n" + elementName + ":");
                                while(attributes.hasNext()) {
                                    System.out.println("\t"
                                        + attributes.next().getValue());
                                }*/

                                name = startElement.getAttributeByName(
                                    new QName("Name")).getValue();

                                break;

                            case "If":
                                ifFlag = true;
                                break;

                            case "Then":
                                thenFlag = true;
                                break;

                            case "Field":
                                path = attributes.next().getValue();
                                break;

                            case "Component":
                                path +=
                                    "[" + attributes.next().getValue() + "]";
                                break;

                            case "Subcomponent":
                                path += "." + attributes.next().getValue();
                                break;

                            case "Value":
                                allowCharReading = true;

                            case "PlainText":
                                valueDataType = elementName;
                                valueDescriptor = "Text";
                                break;

                            case "Regex":
                                valueDataType = "Format";
                                valueDescriptor = "Regex";
                                break;

                            default:
                                continue;
                        }

                        break;

                    case XMLStreamConstants.CHARACTERS:

                        Characters characters = event.asCharacters();

                        String data = characters.getData();

                        if(allowCharReading && (data.trim().length() > 0)) {
                            value = data;
                        }

                        break;

                    case XMLStreamConstants.END_ELEMENT:

                        EndElement endElement = event.asEndElement();

                        elementName = endElement.getName().getLocalPart();

                        //attributes = endElement.getAttributes();

                        switch(elementName) {

                            //finished a segment, write it in
                            case "Value":

                                allowCharReading = false;

                                // at this point, everything needed to define a
                                // constraint is available
                                if(!thenFlag) {
                                    // <ByName Name="">
                                    writer.writeStartElement("ByName");  
                                    writer.writeAttribute("Name", name);

                                    // <Constraint ID="" Target="">
                                    writer.writeStartElement("Constraint");
                                    writer.writeAttribute("ID",
                                        name + "-" + idCounter);
                                    idCounter++;
                                    writer.writeAttribute("Target", path);

                                    // <Description><Description/>
                                    writer.writeStartElement("Description");
                                    writer.writeCharacters("");
                                    writer.writeEndElement();

                                    // <Assertion>
                                    writer.writeStartElement("Assertion");

                                    if(ifFlag) {
                                        writer.writeStartElement("IMPLY");
                                    }
                                }

                                // <Plaintext Path="" Text=""
                                //  IgnoreCase="false"/>
                                // writer will write attr. in alphabetical order
                                writer.writeEmptyElement(valueDataType);
                                writer.writeAttribute("Path", path);
                                writer.writeAttribute(valueDescriptor, value);
                                writer.writeAttribute("IgnoreCase", "false");

                                if(!ifFlag) {
                                    if(thenFlag) {
                                        writer.writeEndElement(); // <IMPLY/>
                                    }

                                    writer.writeEndElement(); // </Assertion>
                                    writer.writeEndElement(); // </Constraint>
                                    writer.writeEndElement(); // </ByName>
                                }

                                

                                break;

                            case "If":
                                ifFlag = false;
                                break;

                            case "Then":
                                thenFlag = false;
                                break;

                            default:
                                continue;
                        }

                    default:
                        continue;
                }
                
            }

            writer.writeEndElement(); // </Constraints>
            writer.writeEndElement(); // </Segment>

            writer.flush();

            // use this to pretty print output.xml
            // OR use xmllint --format output.xml

            TransformerFactory tf = TransformerFactory.newInstance();
            Transformer transformer = tf.newTransformer();

            File outputFormatted = new File(outputFile);
            DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
            DocumentBuilder docBuilder = dbf.newDocumentBuilder();
            Document doc = docBuilder.parse(outputFormatted);

            transformer.setOutputProperty(OutputKeys.INDENT, "yes");
            transformer.setOutputProperty(
                "{http://xml.apache.org/xslt}indent-amount", "4");

            OutputStream outputFinal = new FileOutputStream("outputFinal.xml");

            transformer.transform(new DOMSource(doc), new StreamResult(
                new OutputStreamWriter(outputFinal, "UTF-8")));

        } catch(FileNotFoundException f) {
            System.out.println("" + f);
        } catch(XMLStreamException x) {
            System.out.println("" + x);
        } catch(IOException io) {
            System.out.println("" + io);
        } catch(TransformerConfigurationException tce) {
            System.out.println("" + tce);
        } catch(ParserConfigurationException pce) {
            System.out.println("" + pce);
        } catch(SAXException saxe) {
            System.out.println("" + saxe);
        } catch(TransformerException te) {
            System.out.println("" + te);
        }
    }
}