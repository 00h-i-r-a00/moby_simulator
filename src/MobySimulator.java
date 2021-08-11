import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;

import java.io.*;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.*;

public class MobySimulator {

    private static final String DATA_FILE_PREFIX = "data/";
    private static final String CONFIG_FILE_PREFIX = "data/seeds/";
    private static final String RESULT_FILE_PREFIX = "data/results/";
    private static final String DATA_FILE_FORMAT = ".twr";
    private static final String CONFIG_FILE_FORMAT = ".config";
    private static final String RESULT_FILE_FORMAT = ".csv";
    private static final String QUEUE_OCCUPANCY_FORMAT = ".qo";
    private static final String MESSAGE_DELAYS_FORMAT = ".md";
    private static final String TRUST_SCORE_FILE_FORMAT = ".json";


    private static HashMap<Integer, List<Integer>> networkStateNew = null;
    private static ArrayList<Integer> allTowers = new ArrayList<>();
    private static int timeToLive = 0;
    private static int dosBitsSize;
    private static int dosNumber;
    private static double dosTrust;
    private static boolean trustSimulation;

    private static HashMap<Integer, MobyUser> mobyUserHashMap = new HashMap<>();

    private static Random random;

    public static void main(String[] args){

        // Create all datastructures needed for simulation.
        String configID = "";
        String trustScoreFile = "";
        String configFile = "";
        String resultFile = "";
        String queueOccupancyFile = "";
        String messageDelaysFile = "";
        JsonObject configurationJson = null;
        JsonParser jsonParser = new JsonParser();
        int city;
        int startDay;
        int endDay;
        int seed;
        int queueSize;
        int numberOfDays;
        int threshold;
        int jamTower;
        int jamTowerLogic;
        int jamUser;
        int jamUserLogic;
        int allUserLength;
        int cooldownHours;

        List<Integer> userPool = new ArrayList<>();
        List<Integer> jamTowerList = new ArrayList<>();
        List<Integer> jamUserList = new ArrayList<>();
        List<MobyMessage> messageList = new ArrayList<>();
        String distributionType;
        String slackHook = "";

        JsonArray jsonArray;
        JsonObject jsonObject;
        int i;
        int j;
        int currentDay;
        int currentHour;
        ArrayList<Integer> integerArrayList;
        HashMap<Integer, List<Integer>> networkStateOld = null;
        String currentDataFile;
        boolean firstHour;
        Scanner scanner = null;
        String line;
        String[] parts;
        int hour;
        int towerID;
        String userIDs;
        List<Integer> userSet;
        List<Integer> currentHourUsers;
        int userCounter;
        int simulationHour;
        int messagesInCirculation = 0;
        HashMap<Integer, Integer> messageDelays = new HashMap<>();
        BufferedWriter resultsFileBuffer = null;
        BufferedWriter queueOccupancyFileBuffer = null;
        ArrayList<MobyMessage> deleteList = new ArrayList<>();
        int exchangeProbability = 0;

        try {
            configID = args[0];
        } catch(ArrayIndexOutOfBoundsException e) {
            System.out.println("Please pass a configuration ID!!");
            return;
        }

        // Build all input output filenames.
        configFile = CONFIG_FILE_PREFIX + configID + CONFIG_FILE_FORMAT;
        resultFile = RESULT_FILE_PREFIX + configID + RESULT_FILE_FORMAT;
        queueOccupancyFile = RESULT_FILE_PREFIX + configID + QUEUE_OCCUPANCY_FORMAT;
        messageDelaysFile = RESULT_FILE_PREFIX + configID + MESSAGE_DELAYS_FORMAT;
        System.out.println("Configuration file: " + configFile);


        // Get config JSON from file.
        try {
            configurationJson = jsonParser.parse(new FileReader(configFile)).getAsJsonObject();
        } catch (FileNotFoundException e) {
            System.out.println("Invalid config file supplied!!");
            return;
        }


        // Read in all required configurations
        city = configurationJson.get("city").getAsInt();
        startDay = configurationJson.get("start-day").getAsInt();
        endDay = configurationJson.get("end-day").getAsInt();
        seed = configurationJson.get("seed").getAsInt();
        queueSize = configurationJson.get("queuesize").getAsInt();
        threshold = configurationJson.get("threshold").getAsInt();
        dosNumber = configurationJson.get("dos-number").getAsInt();
        jamTower = configurationJson.get("jam-tower").getAsInt();
        jamTowerLogic = configurationJson.get("jam-tower-logic").getAsInt();
        jamUser = configurationJson.get("jam-user").getAsInt();
        jamUserLogic = configurationJson.get("jam-user-logic").getAsInt();
        numberOfDays = endDay - startDay;
        cooldownHours = configurationJson.get("cooldown").getAsInt();
        trustScoreFile = DATA_FILE_PREFIX + configurationJson.get("trust-scores").getAsString() + TRUST_SCORE_FILE_FORMAT;
        trustSimulation = configurationJson.get("trust-simulation").getAsBoolean();

        // Seed the random to make picking subsets in MX reproducible
        random = new Random(seed);

        try {
            exchangeProbability = configurationJson.get("exchange-probability").getAsInt();
        } catch (java.lang.UnsupportedOperationException e) {
            exchangeProbability = 0;
        }

        try {
            slackHook = configurationJson.get("slack-hook").getAsString();
        } catch (java.lang.UnsupportedOperationException e) {
            System.out.println("Slack hook missing, won't send messages!");
        }

        // Convert messages to our own objects.
        jsonArray = configurationJson.get("messages").getAsJsonArray();
        for(i = 0; i < jsonArray.size(); i++) {
            jsonObject = (JsonObject) jsonArray.get(i);

            if(i == 0) timeToLive =  jsonObject.get("ttl").getAsInt();
            // Enforce unchanging TTL here?

            messageList.add(new MobyMessage(
                    jsonObject.get("id").getAsInt(),
                    jsonObject.get("ttl").getAsInt(),
                    jsonObject.get("src").getAsInt(),
                    jsonObject.get("dst").getAsInt(),
                    jsonObject.get("hour").getAsInt(),
                    1.0
            ));
        }

        jsonArray = configurationJson.get("userpool").getAsJsonArray();
        for(i = 0; i < jsonArray.size(); i++) {
            userPool.add(jsonArray.get(i).getAsInt());
        }

        jsonArray = configurationJson.get("jam-user-list").getAsJsonArray();
        for(i = 0; i < jsonArray.size(); i++) {
            jamUserList.add(jsonArray.get(i).getAsInt());
        }

        jsonArray = configurationJson.get("jam-tower-list").getAsJsonArray();
        for(i = 0; i < jsonArray.size(); i++) {
            jamTowerList.add(jsonArray.get(i).getAsInt());
        }

        jsonArray = configurationJson.get("all-towers").getAsJsonArray();
        for(i = 0; i < jsonArray.size(); i++) {
            allTowers.add(jsonArray.get(i).getAsInt());
        }

        // Deal with default queue size.
        if(queueSize == 0) {
            System.out.println("Default queuesize, using:" + messageList.size());
            queueSize = messageList.size();
        }

        // Done with the configuration json!
        configurationJson = null;
        firstHour = true;

        System.out.println("Creating per user hashmaps :" + userPool.size());
        // 1 bit = dosnumber of bits, so just need one bit per hour per tower.
        dosBitsSize = allTowers.size() * ((numberOfDays * 24) - cooldownHours);
        for(int user : userPool) {
            MobyUser mobyUser = new MobyUser(user, queueSize, dosNumber, messageList.size(), dosBitsSize);
            mobyUserHashMap.put(user, mobyUser);
        }

        // Load trust scores from file.
        if(!trustScoreFile.isEmpty() && trustSimulation) {
            try {
                JsonObject trustScoreJson = jsonParser.parse(new FileReader(trustScoreFile)).getAsJsonObject();
                jsonArray = trustScoreJson.getAsJsonArray("users");
                System.out.println("Got trust scores for: " + jsonArray.size());
                JsonObject element;
                JsonArray trustedArray;
                MobyUser mobyUser;
                int user;
                for(i = 0; i < jsonArray.size(); i++) {
                    element = jsonArray.get(i).getAsJsonObject();
                    user = Integer.parseInt((String)element.keySet().toArray()[0]);
                    mobyUser = mobyUserHashMap.get(user);
                    if(mobyUser == null)
                        continue;
                    trustedArray = element.getAsJsonArray("" + user);
                    for(j = 0; j < trustedArray.size(); j++) {
                        mobyUser.setUserTrust(trustedArray.get(j).getAsInt(), 1.0);
                    }
                }
                dosTrust = 0.0;
            } catch (FileNotFoundException e) {
                System.out.println("Invalid trust score file supplied!!");
                return;
            }
        } else {
            dosTrust = 0.0;
        }

        // Parse towers file and get all information.
        networkStateOld = new HashMap<>();

        // Open results file and queue occupancy file.
        try {
            resultsFileBuffer = new BufferedWriter(new FileWriter(resultFile));
            queueOccupancyFileBuffer = new BufferedWriter(new FileWriter(queueOccupancyFile));
        } catch (IOException e) {
            System.out.println("Problem opening results file or queue occupancy file!!");
        }
        // For the range of days.
        for(currentDay = startDay; currentDay < endDay; currentDay ++) {
            // For the hours of a day.
            for(currentHour = 0; currentHour < 24; currentHour++) {
                networkStateNew = new HashMap<>();
                currentHourUsers = new ArrayList<>();
                simulationHour = currentHour + (24 * (currentDay - startDay));

                if(threshold==0)
                    currentDataFile = DATA_FILE_PREFIX + city + "/" + currentDay + "_" + currentHour + DATA_FILE_FORMAT;
                else
                    currentDataFile = DATA_FILE_PREFIX + city + "_" + threshold + "/" + startDay + "/" + numberOfDays +
                            "/" + currentDay + "_" + currentHour + DATA_FILE_FORMAT;

                if(!firstHour){
                    System.out.println("Message delivery count: " + messageDelays.size() + " of: " + messagesInCirculation);
                    System.out.println("Delivery rate: " + (double) messageDelays.size() / messagesInCirculation);
                } else
                    firstHour = false;

                System.out.println("Processing hour: " + currentHour + " File: " + currentDataFile);
                try {
                    scanner = new Scanner(new File(currentDataFile));
                } catch(FileNotFoundException e) {
                    System.out.println(e.toString());
                }

                userCounter = 0;

                while(scanner.hasNext()) {
                    line = scanner.nextLine();
                    parts = line.split(",");
                    hour = Integer.parseInt(parts[0]);
                    towerID = Integer.parseInt(parts[1]);
                    userIDs = parts[2];
                    userSet = new ArrayList<>();

                    for (String user : userIDs.split("\\|")) {
                        userSet.add(Integer.parseInt(user));
                    }

                    userCounter += userSet.size();
                    networkStateNew.put(towerID, userSet);
                    currentHourUsers.addAll(userSet);
                }
                scanner.close();

                System.out.println("Total users seen this hour: " + userCounter);
                System.out.println("Unique users seen this hour: " + currentHourUsers.size());
                System.out.println("Userset new people: " + userPool.containsAll(currentHourUsers));

                // Send out messages for this hour.
                // TODO: Might be a better way to do this than parse the entire list of messages.
                for(MobyMessage m : messageList) {
                    if(m.hour == simulationHour) {
                        // System.out.println("Source: " + mobyUserHashMap.get(m.src));
                        mobyUserHashMap.get(m.src).addMessage(m.id, 1.0);
                        messagesInCirculation += 1;
                    }
                }

                // Jam towers based on the jam tower list provided by generate messages.
                for (int jamTowerID : jamTowerList) {
                    networkStateNew.remove(jamTowerID);
                }

                // At this point, the old simulator would figure out who moved and things like that, that's unnecessary imo.
                List<Integer> sortedList = new ArrayList<>();
                sortedList.addAll(networkStateNew.keySet());
                Collections.sort(sortedList);

                // Simulation message exchanges.
                if (exchangeProbability > 0 && exchangeProbability < 100) {
                  partialMXHandler(sortedList, simulationHour, dosNumber, queueSize, exchangeProbability);
                } else {
                  messageExchangeHandler(sortedList, simulationHour, dosNumber, queueSize);
                }

                // Check message deliveries.
                for(MobyMessage m : messageList) {
                    if(!m.getDelivered()) {
                        try {
                            // TODO: This could be moved to checking the bitset instead.
                            if(mobyUserHashMap.get(m.dst).hasMessage(m.id)) {
                                m.setDelivered();
                                messageDelays.put(m.id, simulationHour - m.hour);
                                System.out.println("Message: " + m.id + " Delay: " + (simulationHour - m.hour));
                            }
                        } catch (NullPointerException e) {
                            System.out.println("Exception: " + e.toString());
                            // Dead user!!
                        }
                    }
                }

                // Write delivery ratio.
                try {
                    resultsFileBuffer.write(
                            currentDay + "," +
                                    currentHour + "," +
                                    currentHourUsers.size() + "," +
                                    messageDelays.size() + "," +
                                    messagesInCirculation + "," +
                                    timeToLive + "," +
                                    queueSize + "," +
                                    dosNumber + "," +
                                    trustSimulation + "," +
                                    trustScoreFile + "," +
                                    seed + "," +
                                    threshold + "," +
                                    configID + '\n');
                } catch (IOException e) {
                    System.out.println("Problem writing delivery ratios!!");
                }

                // Write queue occupancy.
                try {
                    int totalDosMessages = 0;
                    int totalNonDos = 0;
                    MobyUser mobyUser;
                    for(int user : currentHourUsers) {
                        mobyUser = mobyUserHashMap.get(user);
                        totalDosMessages += (mobyUser.getDosSetSize() * dosNumber);
                        totalNonDos += mobyUser.getQueueOccupancy(0);
                        queueOccupancyFileBuffer.write(
                                currentDay + "," +
                                        currentHour + "," +
                                        user + "," +
                                        mobyUser.getQueueOccupancy(dosNumber) + '\n');
                    }
                    // Don't think I really need this anywhere. Might be expensive computing it.
                    System.out.println("Avg. DOS occupancy: " + totalDosMessages/currentHourUsers.size());
                    System.out.println("Avg. Non Dos occupancy: " + totalNonDos/currentHourUsers.size());
                } catch (IOException e) {
                    System.out.println("Problem writing queue occupancies!!");
                }

                // Reduce TTLs and drop messages.
                System.out.println("TTL check!");
                deleteList.clear();
                for(MobyMessage m : messageList) {
                    if(m.hour <= simulationHour) {
                        m.ttl--;
                        if(m.ttl < 0)
                            deleteList.add(m);
                    }
                }

                System.out.println("Deleting " + deleteList.size() + " dead messages!!");
                for(MobyMessage m : deleteList) {
                    messageList.remove(m);
                }

                int canParticipate = 0;

                for(Map.Entry<Integer, MobyUser> userEntry : mobyUserHashMap.entrySet()) {
                    userEntry.getValue().deleteMessages(deleteList);
                    if(simulationHour > timeToLive) {
                        int clearIndex = ((allTowers.size()) * (simulationHour - timeToLive));
                        clearIndex -= 1;
                        userEntry.getValue().dropDos(clearIndex);
                    }
                }

                networkStateOld = networkStateNew;
                // Do next hour.
            }
            // Do next day.
            // sendSlackMessage(slackHook, "Day: " + currentDay + " done!!");
        }

        // Close results file and queue occupancy file.
        try {
            resultsFileBuffer.close();
            queueOccupancyFileBuffer.close();
        } catch (IOException e) {
            System.out.println("Problem closing results file or qo file!!");
        }

        // Write message delays.
        try {
            BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(messageDelaysFile));
            Iterator iterator = messageDelays.entrySet().iterator();
            while(iterator.hasNext()) {
                HashMap.Entry entry = (HashMap.Entry)iterator.next();
                bufferedWriter.write(entry.getKey().toString() + "," + entry.getValue().toString() + '\n');
            }
            bufferedWriter.close();
        } catch(IOException e) {
            System.out.println("IOException at writing message delays file!!");
        }

        // Simulation done, send message to slack.
        String msg = "Simulation ttl: " + timeToLive + ", dosNumber: " + dosNumber + ", delivery ratio: " + ((float)messageDelays.size() / messagesInCirculation) + ", config: " + configID;
        sendSlackMessage(slackHook, msg);

    }

    private static void sendSlackMessage(String slackHook, String message) {
        if(slackHook.isEmpty())
            return;
        System.out.println("Sending slack message!!");
        String payload = null;
        HttpPost httpPost = new HttpPost(slackHook);
        httpPost.setHeader("Content-type", "application/json");
        CloseableHttpClient httpClient = HttpClients.createDefault();
        try {
            payload = "{ \"text\": \"" + message + " Host: " + InetAddress.getLocalHost().getHostName()  + " \"}";
            httpPost.setEntity(new StringEntity(payload));
            CloseableHttpResponse closeableHttpResponse  = httpClient.execute(httpPost);
            if(closeableHttpResponse.getStatusLine().getStatusCode() == 200)
                System.out.println("Successful post to slack!!");
            else
                System.out.println("Failed trying to post to slack!!");
            closeableHttpResponse.close();
        } catch (UnknownHostException e) {
            System.out.println("Unknown host!!");
        } catch (UnsupportedEncodingException e) {
            System.out.println("Unsupported encoding!!");
        } catch (IOException e) {
            System.out.println("IOException!!");
        }
    }

    private static void partialMXHandler(List<Integer> towerIDs, int simulationHour,
                                         int dosNumber, int queueSize, int exchangeProbability) {
        System.out.println("Sim hour:" + simulationHour + ", TTL:" + timeToLive +
                ", Dos: " + dosNumber + ", QS: " + queueSize);

        // Perform exchanges just one way.
        for (int tower : towerIDs) {
            List<Integer> usersInTower = networkStateNew.get(tower);
            Collections.sort(usersInTower);
            for (int u1 : usersInTower) {
                for (int u2: usersInTower) {
                    if (u1 == u2) continue;
                    
                    if (random.nextInt(100) < exchangeProbability) {
                        MobyUser mobyUser1 = mobyUserHashMap.get(u1);
                        MobyUser mobyUser2 = mobyUserHashMap.get(u2);

                        mobyUser1.performMessageExchangeTailDrop(mobyUser2, dosNumber, -1);
                        mobyUser2.performMessageExchangeTailDrop(mobyUser1, dosNumber, -1);
                    }
                }
            }
        }
    }

    //Message exchange handler
    private static void messageExchangeHandler(List<Integer> towerIDs, int simulationHour,
                                        int dosNumber, int queueSize){

        System.out.println("Sim hour:" + simulationHour + ", TTL:" + timeToLive +
                ", Dos: " + dosNumber + ", QS: " + queueSize);

        int dosIDForHour = -1;

        System.out.println("Performing exchange 1 way");
        // Perform exchanges one way.
        for(int tower : towerIDs) {
            if(dosNumber > 0)
                dosIDForHour = (allTowers.size() * simulationHour) + allTowers.indexOf(tower);
            performMessageExchange(networkStateNew.get(tower), dosIDForHour);
        }

        // Reverse tower order.
        Collections.reverse(towerIDs);

        System.out.println("Performing exchange other way");
        // Perform exchanges the other way.
        for(int tower : towerIDs) {
            if(dosNumber > 0)
                dosIDForHour = (allTowers.size() * simulationHour) + allTowers.indexOf(tower);
            performMessageExchange(networkStateNew.get(tower), dosIDForHour);
        }
    }

    // Perform message exchange in tower
    private static void performMessageExchange(List<Integer> users, int dosIDForHour){
        // For all pairs of users, send messages from one queue to the other with queue constraints in mind.
        MobyUser mobyUser1, mobyUser2;
        Collections.sort(users);
        for (int u1 : users) {
            mobyUser1 = mobyUserHashMap.get(u1);
            mobyUser1.performDosExchangeForHour(dosIDForHour, dosNumber);
            for (int u2 : users) {
                mobyUser2 = mobyUserHashMap.get(u2);
                mobyUser1.performMessageExchangeTailDrop(mobyUser2, dosNumber, dosIDForHour);
            }
        }

    }
}

class MobyMessage {
    int id;
    int ttl;
    int src;
    int dst;
    int hour;
    double trust;
    private boolean delivered;


    public MobyMessage(int identifier, int timeToLive, int source, int destination,
                       int hourSent, double trustScore) {
        this.id = identifier;
        this.ttl = timeToLive;
        this.src = source;
        this.dst = destination;
        this.hour = hourSent;
        this.trust = trustScore;
        this.delivered = false;
    }

    public void setDelivered() {
        this.delivered = true;
    }

    public boolean getDelivered() {
        return this.delivered;
    }
    // Use this to store delivered information?
}

class MobyUser {
    private int uid; // Unique ID for each user in the simulation.
    private HashMap<Integer, Double> messageQueue; // Message queue for this user.
    private HashMap<Integer, Double> trustScores;
    private BitSet messageQueueBits;
    private BitSet dosQueueBits = null;
    private int queueSize = 0;
    private Random random;

    public MobyUser(int userID, int queueSize, int dosNumber, int messageQueueSize, int dosQueueSize) {
        this.uid = userID;
        this.queueSize = queueSize;
        this.messageQueue = new HashMap<>();
        this.messageQueueBits = new BitSet(messageQueueSize);
        if (dosQueueSize > 0)
            this.dosQueueBits = new BitSet(dosQueueSize);
        trustScores = new HashMap<Integer, Double>();
        this.random = new Random(userID);
    }

    public BitSet getMessageQueueDifference(MobyUser mobyUser) {
        BitSet difference = this.getMessageQueueBitsClone(); // Copy my own bitset.
        difference.or(mobyUser.getMessageQueueBits()); // Calculate union of two bitsets.
        difference.andNot(this.messageQueueBits); // Union of bitsets - my bitset.

        return difference;
    }

    public BitSet getDosQueueDifference(MobyUser mobyUser) {
        BitSet difference = (BitSet) this.dosQueueBits.clone();
        difference.or(mobyUser.getDosQueueBits());
        difference.andNot(this.dosQueueBits);
        return difference;
    }

    public BitSet getDosQueueBits() {
        return this.dosQueueBits;
    }

    public BitSet getMessageQueueBitsClone() {
        return (BitSet) this.messageQueueBits.clone();
    }

    public BitSet getMessageQueueBits() {
        return this.messageQueueBits;
    }

    public int getFreeSpace(int dosNumber) {
        if(dosNumber > 0)
            return this.queueSize - (this.messageQueueBits.cardinality() + (this.dosQueueBits.cardinality() * dosNumber));
        return this.queueSize - this.messageQueueBits.cardinality();
    }

    public int getQueueOccupancy(int dosNumber) {
        if(dosNumber > 0)
            return this.messageQueueBits.cardinality() + (this.dosQueueBits.cardinality() * dosNumber);
        return this.messageQueueBits.cardinality();
    }

    public void dropDos(int index) {
        this.dosQueueBits.clear(0, index);
    }

    public void addMessage(int messageID, double trust) {
        this.messageQueue.put(messageID, trust);
        this.messageQueueBits.set(messageID);
    }

    public boolean hasMessage(int messageID) {
        return this.messageQueueBits.get(messageID);
    }

    public void deleteMessages(ArrayList<MobyMessage> messages) {
        for(MobyMessage message : messages) {
            this.messageQueueBits.clear(message.id);
            this.messageQueue.remove(message.id);
        }
    }

    public HashMap<Integer, Double> getMessageQueue() {
        return this.messageQueue;
    }

    public int getUID() { return this.uid; }

    public void setUserTrust(int userID, double trust) { this.trustScores.put(userID, trust); }

    // Return 1 for now, but implement trust lookup here.
    public double getUserTrust(int userID) { return this.trustScores.getOrDefault(userID, 1.0); }

    public void performDosExchangeForHour(int dosIDForHour, int dosNumber) {
        int freeSpace = this.getFreeSpace(dosNumber);
        if (freeSpace > 0 && dosIDForHour != -1)
            this.dosQueueBits.set(dosIDForHour);
    }

    public void performMessageExchangeTailDrop(MobyUser mobyUser, int dosNumber, int dosIDForHour) {
        double trust = this.getUserTrust(mobyUser.getUID());
        if (trust == 0)
            return;
        BitSet newMessages = this.getMessageQueueDifference(mobyUser);
        int freeSpace = this.getFreeSpace(dosNumber);
        HashMap<Integer, Double> mobyUserMessages = mobyUser.getMessageQueue();

        // Dos Sim!
        if(dosIDForHour != -1) {
            // First exchange dos messages, as many as we have space to accomodate.
            BitSet newDosMessages = this.getDosQueueDifference(mobyUser);
            for(int bitIndex = newDosMessages.nextSetBit(0);
                bitIndex != -1 && freeSpace > 0; // Try filling queue as much as possible.
                bitIndex = newDosMessages.nextSetBit(bitIndex)) {
                this.dosQueueBits.set(bitIndex);
                freeSpace -= dosNumber;
            }
        }

        // Now handle new legit messages.
        for(int bitIndex = newMessages.nextSetBit(0);
            bitIndex >= 0 && freeSpace > 0 ; bitIndex = newMessages.nextSetBit(bitIndex+1)) {
            this.messageQueueBits.set(bitIndex);
            freeSpace -= 1;
        }

    }

    public void performMessageExchangeRandomDrop(MobyUser mobyUser, int dosNumber, int dosIDForHour) {
        double trust = this.getUserTrust(mobyUser.getUID());
        if(trust == 0)
            return;
        BitSet newMessages = this.getMessageQueueDifference(mobyUser);
        BitSet newDosMessages = this.getDosQueueDifference(mobyUser);
        HashMap<Integer, Double> mobyUserMessages = mobyUser.getMessageQueue();

        // Exchange MQ
        for(int bitIndex = newMessages.nextSetBit(0);
            bitIndex != -1;
            bitIndex = newMessages.nextSetBit(bitIndex + 1)) {
            // My trust = other user's trust * trust in them.
            this.messageQueue.put(bitIndex, mobyUserMessages.get(bitIndex) * trust);
            this.messageQueueBits.set(bitIndex);
        }

        // Not a Dos Sim!
        if(dosIDForHour == -1){
            this.performRandomDrop(dosNumber);
            return;
        }

        // Exchange DosQueue
        for(int bitIndex = newDosMessages.nextSetBit(0);
        bitIndex != -1;
        bitIndex = newDosMessages.nextSetBit(bitIndex + 1)) {
            this.dosQueueBits.set(bitIndex);
        }

        this.performRandomDrop(dosNumber);
    }

    public void performRandomDrop(int dosNumber) {
        //
        int freeSpace = this.getFreeSpace(dosNumber);

        if (freeSpace >= 0)
            return;

        freeSpace *= -1;
        int drop;
        double dosProb;
        while (freeSpace > 0) {
            dosProb = ((double) (dosQueueBits.cardinality() * dosNumber)) / ((dosQueueBits.cardinality() * dosNumber) + messageQueueBits.cardinality());
            if (random.nextDouble() > dosProb) {
                freeSpace -= 1;
                drop = messageQueueBits.nextSetBit(0);
                messageQueueBits.clear(drop);
                messageQueue.remove(drop);
            } else {
                freeSpace -= dosNumber;
                drop = dosQueueBits.nextSetBit(0);
                dosQueueBits.clear(drop);
            }
        }
    }

    public int getDosSetSize() { return this.dosQueueBits.cardinality(); }

}
