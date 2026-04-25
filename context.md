Your Role: you are a Django Backend Engineer

Task: create Following backend. ui is given in figma

both frontend and backend has been created. admin panel(next.js) and mobile frontend(flutter)

now create folling apis. what keep extra datas, you can use djaog or drf but create apis that can be intrigated in both moth mobiles and in admin panel. is is a role based app. admin can take multiple action, and it has pricing stuff



you will create thigns step by step. in one action you will create models, serializer apis and steps to implement it

for authentication use jwt,

and keep things simple don't add extra stuff. try keeps things professional and modular

figma desing: https://www.figma.com/proto/DHTaNIub2Hs0gnFZ61ufDA/icsncardio-%7C%7C-heartbeat-harmony?node-id=0-1\&t=rJ6KWuRKzmD8zjRs-1







admin panel(next.js): https://heart-wellness.vercel.app/



again i am gonna give you overview:



this app will calculate Heart Balance based on how he felling(joyfull, calm, hopefull, Netral, Anxious, Sad, streesed, Tried), Rating(Mental Clarity, Emotional Balance, Spiritural wellness, physical energy), Gratitude text(can be avoid during scoring), Notes(can be avoid during scoring)



there will be four main page:



**Homepage:** previous all things under home page

**Habit page:** User will be able to create habit(up to 3 havit creation will be free)

in each habit following thigs mush have(Category, Acitivity Name, Description, Duration)

\*\*Study page:\*\*it will show list of study and its progress,  there are two section in study page(quiz, Materail). admin will be able to add (quiz, study material).user will be able to download study material, quiz will be mcq question there will be 4 question user will select one ,

Community Page: here user will be able to both community chat and one to one chat,

Page description:

home: dashboard-> spiritual rating, Mental rating, Physical rating, Emotional Rating and overall scrore. after this cart there will be few section(Daily Habits, Message, progress), Practice question section, Unlock Premium,

how are you felling may be under home page: modes

rating page :user can rate on Mental clarity, emotional Balance, Spiritual Wellness, Physical Energy

Gratitute page: user can add text

Note page: user can add text here

Calculated Hart balance: total rating



**Habit page:**

Habit page: user can see habits

create habit page: user can select a category, Activity name, Description of the habit, duration (kind of like form)



**Study Page:**

study page: list of study projecess cart(or row),

question ans page: user can ans mcq;

quiz complete : show total quiz mark,

study Material page: user can see list of study metarials,

study metarial detail page: user can click one stude metarl and read pdf/text or stuff



Community:



community page: user can see comminty and one to one person to chate or to share things in the chat,

chat page: user can click a person and can chat in this page

premium pricing page: user can see premium plans and advantares of premium planes,



**Profile page:**



profile page: user can see his check-ins, study hours, rank



personal deatals change page: Name, username, email address, phone number,



progress page: user can see his total progress



check in history page: user can see list total check in history by weekly, mothly, or earyly



check in history details: user can see detal check in history after click in any list of the check in history page(that user inputed before)

password change page: user can change password



privacy policy page: user can see texts

&#x20;help and support page:





===========================================

**Admin Panel: (not for mobile)**



authentication section : admin login, forgot password, verification and Reset Password



Dashboard:hard balance trend(combining all user), mode distribution(combining all users mood),user insigh



User Management Page

amdin can see users name, image, email, phone number, plna, status, action; admin can take an action he can edit stuffs or can delete user



check in: admin  review check ins \& can take action as well,

Category: admin can see category and can add category,



Mode Scoring: admin can see moods of user and also can create new mood

Study Scoring : admin can see topics name and score

Study Materials: admin can create new Materails and also can take action on each material means admin can  go edit stuff

Quiz Test: admin can see quiz result by user and also can create new quize(mcq)



pricing: admin can create pricing and add facilies with it



settings: where admin can change password, name, email, Name

======================

Lets go

