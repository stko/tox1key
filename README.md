# Tox 1Key - the decentralized door opening (=access control) system

WTF is a decentralized door opening system? In the moment it is just a weird proof-of-concept-in-progress, born out of a conflictive set of wishes for a door opening system (which stands here representative for access control in general).

So let us use a door to explain: A door has a lock, and some keys do match that lock. Some people owns these keys, so they can open the door whenever they want.

That principle is proved now since centuries, and it works as long as it's static, and as long it is ok that all the people have access all the time.



The hassle starts when the group of people or the entry times become flexible. You know it from your own life: You want to do some housekeeping at your friends while they are on holiday the next two weeks, a craftsman wants to enter your home while you are at work, the parcel service wants to store some deliveries, you want to pick up something at your parents, but you can't make it by yourself and ask your friend to do and so on. The cases are endless, and all the time you would need to give your key away to somebody else and to wait, that you'll get it back, while in the meantime you are without a key for yourself.

On public or shared buildings it's even more complicated: A lot of people need to get in for different reasons at different times, a lot of copied keys flying around all over the place, some of them get lost, become borrowed to others, so in the end of the day nobody knows anymore where are all the keys are.

And even if you move from the medieval hardware key to the 21st century smart door and a door opening app, you still facing problems:
- there are so many different systems on the market. For each combination you and your actual counterpart need to have the right application on the mobile, everybody need to have the right accounts and need to have the skill to handle all this correctly and effective
- and even then either you as a system owner or the person, who want to grant access will need to reconfigure the opening system all the time to allow new people, changing times or take some temporary permissions out again.


This is where Tox1Key comes in place..

## The unique advantages of Tox1Key
Before looking into Tox1Key itself, let us first summarize the benefits of using [Tox](https://tox.org) as backbone architecture:
1. Fully decentralized, so no dependency on any vulnerable central servers
2. Open source, so no dependency on any single supporting company or organisation
3. No data is stored on any servers, only on the user clients itself
4. no information exchange to unknown persons, only between registered friends

This and the well done programming interface makes Tox to the ideal platform to build Tox1Key on top of it.

### How does Tox1key work?  
It's starts with the door lock: When you initially set up a tox1key door opening system, you configure the "root owners" of this door by their ToxID. Also the door lock itself becomes an (automated) Tox client.

So after initial set up, only these people can open the door - but in Tox1Key, and that's the trick, each user can share his access rights:

So let us give such a user a name and call her Alice (what a surprise....). Now Alice want to give access to (guess who ..) Bob.

She opens her Tox1Key app, selects the right door out of her list of accessible doors and finds Bob by his ToxID in the Tox network.

Then she grants Bob a time slot in her calendar view, similar like a meeting schedule, let's say Mo 10:00-12:00 (unique or regularly)

This information, that Alice shares a timeslot with Bob, is then send to the door. The door noticed that the permitted user Alice has defined a new time slot for the formerly unknown user Bob, so it stores the time slot and also sends a friends request to Bob. After he has confirmed the request, the calendar data is been transmitted to Bob, so he can see in his calendar that he can open the door on Monday from 10-12.

If the build in depth-counter does not forbid that, then Bob can also share his time slot with Carol in the same way. The door saves the information, that Bob shares with Carol, invides Carol and so on.

Now Carol wants to enter the door: She sends a boarding pass request to the door for a time slot. The door defines a random code nr for this, stores it and sent it back to Carol. This is for that Carol can get her entry code in advance before reaching the door and is not depending on a working internet connection when she stands in the cold rain in front of the door without internet access. Also for e.g. parcel services time is money and a clever client software could request the entry code already when coming close to where the door is.


When then standing in front of the door, Carol presents her entry code e.g. as QR-Code to a camera or via NFC. Then door then identifies Carol by her stored entry code. Then the door run through the permission tree: Is Carol permitted by Bob to enter now **and** is Bob permitted by Alice to enter now **and** is Alice permitted as well?

When this "permission dependency tree" test passes, then the door is opened.

### Deletion of Users and time slots
Let's assume Alice don't want to let Bob in anymore. She either moves his time slot or his whole account into the paper bin. The paper bin concept is used instead of a direct deletion to leave the user the choice to undo the deletion, as it will create a lot of confusion and work when accidently destroy a lot of dependent timeslots.

This deletion marker is transferred to the door, so that the deletion becomes active instantly. When receiving such a deletion, the door runs through the whole permission tree and marks all affected users and timeslots as been deleted. This is also reported to the users, so that they are aware.


If then the deletion get's finally active after reaching the timeout in the paper bin or by actively selected by the user, the door finally runs through the permission tree, deletes all entries and sends a final deletion notification to the affected users before remove them out of the friends list.



### Data visibility
The visible information are limited: A user can only see, which time frames he got from another user, but he can't see from who that user got his "parent" time frames. Also he can only see to who he shares his time slots with, but he can't see to who this slots have been shared further.

