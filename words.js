// Word of the day — one word for every calendar day (366, including Feb 29).
// Format: [English, Chinese, pinyin, Spanish, kid definition, example sentence]
// MONTHS[m][d-1] is the word for month m (0 = January), day d.
// To change a word, edit its line and push. Keep every month the right length.

window.WOTD = {};

WOTD.MONTHS = [
// ── January: winter and new beginnings (31) ──
[
["calendar","日历","rìlì","el calendario","A chart of all the days, weeks, and months in a year.","We hung up a brand-new calendar for the new year."],
["snowflake","雪花","xuěhuā","el copo de nieve","One tiny piece of snow. No two are exactly alike.","A snowflake landed on her nose and melted."],
["mitten","连指手套","liánzhǐ shǒutào","la manopla","A warm glove that keeps all your fingers together.","She lost one mitten somewhere in the snow."],
["scarf","围巾","wéijīn","la bufanda","A long soft cloth you wrap around your neck to stay warm.","Grandma knitted me a bright red scarf."],
["icicle","冰柱","bīngzhù","el carámbano","A pointy stick of ice that hangs down from a roof.","A long icicle dripped from the edge of the roof."],
["igloo","冰屋","bīngwū","el iglú","A round house made out of blocks of snow.","We built a tiny igloo for our toy bear."],
["polar bear","北极熊","běijíxióng","el oso polar","A big white bear that lives where it is icy and cold.","The polar bear slid down the snowy hill on its belly."],
["snowman","雪人","xuěrén","el muñeco de nieve","A person you build out of big balls of snow.","Our snowman had a carrot nose and button eyes."],
["sled","雪橇","xuěqiāo","el trineo","A flat seat that slides fast down snowy hills.","We zoomed down the hill on a red sled."],
["blanket","毯子","tǎnzi","la manta","A big soft cover that keeps you warm.","We made a fort out of every blanket in the house."],
["fireplace","壁炉","bìlú","la chimenea","A place in the wall of a house where a fire keeps you warm.","We toasted marshmallows by the fireplace."],
["owl","猫头鹰","māotóuyīng","el búho","A bird with big round eyes that stays awake at night.","An owl hooted from the tall tree."],
["fox","狐狸","húli","el zorro","A clever animal with orange fur and a fluffy tail.","A fox tiptoed across the snowy yard."],
["pinecone","松果","sōngguǒ","la piña de pino","The bumpy brown seed holder that falls from a pine tree.","The squirrel carried a pinecone up the tree."],
["frost","霜","shuāng","la escarcha","Thin white ice that covers the grass on cold mornings.","The frost made the car window sparkle."],
["boots","靴子","xuēzi","las botas","Tall shoes that keep your feet dry in snow and rain.","She stomped through the slush in her boots."],
["soup","汤","tāng","la sopa","A warm food made of liquid that you eat with a spoon.","Hot soup warmed us up after playing outside."],
["pajamas","睡衣","shuìyī","el pijama","Soft clothes you wear to bed.","He wore his dinosaur pajamas all day long."],
["bear","熊","xióng","el oso","A big furry animal that sleeps through the winter.","The bear curled up in its den until spring."],
["wool","羊毛","yángmáo","la lana","The soft, curly hair of a sheep, used to make sweaters.","My warm socks are made of wool."],
["sweater","毛衣","máoyī","el suéter","A warm, fuzzy shirt with long sleeves.","Daddy's sweater was way too big for me."],
["moose","驼鹿","tuólù","el alce","A giant deer with huge, flat antlers.","The moose waded through the icy river."],
["hot cocoa","热可可","rè kěkě","el chocolate caliente","A warm, sweet chocolate drink.","We blew on our hot cocoa to cool it down."],
["ice skate","溜冰鞋","liūbīngxié","el patín de hielo","A boot with a blade that lets you glide on ice.","She wobbled on her ice skates, then zoomed away."],
["seal","海豹","hǎibào","la foca","A slippery ocean animal with flippers that barks.","The seal clapped its flippers for a fish."],
["walrus","海象","hǎixiàng","la morsa","A big sea animal with two long white tusks.","The walrus napped on a block of ice."],
["glove","手套","shǒutào","el guante","A warm cover for your hand with a spot for each finger.","I wiggled all ten fingers into my gloves."],
["lamp","台灯","táidēng","la lámpara","A light you turn on so you can see in the dark.","Mommy turned on the lamp to read me a story."],
["north","北方","běifāng","el norte","The direction at the very top of a map.","The cold wind blew in from the north."],
["husky","哈士奇","hāshìqí","el husky","A strong, fluffy dog that pulls sleds through the snow.","The husky dogs pulled the sled across the ice."],
["cabin","小木屋","xiǎo mùwū","la cabaña","A small house made of logs.","We stayed in a cozy cabin in the woods."]
],
// ── February: love, friends, and cozy things (29 — the 29th only shows in leap years) ──
[
["heart","心","xīn","el corazón","The part in your chest that goes thump-thump. It is also a shape that means love.","She drew a big red heart for her mommy."],
["groundhog","土拨鼠","tǔbōshǔ","la marmota","A furry animal that digs holes and pops out of the ground.","The groundhog peeked out and saw its shadow."],
["friend","朋友","péngyou","el amigo","Someone you like to play with and care about.","My friend shared her crayons with me."],
["hug","拥抱","yōngbào","el abrazo","When you wrap your arms around someone you love.","Grandpa gave me a big squeezy hug."],
["card","卡片","kǎpiàn","la tarjeta","A folded piece of paper with a picture and a message.","We made a card with glitter and stickers."],
["rose","玫瑰","méigui","la rosa","A beautiful flower with soft petals and a prickly stem.","Daddy brought Mommy a red rose."],
["cupcake","纸杯蛋糕","zhǐbēi dàngāo","el pastelito","A little cake baked in a paper cup.","Her cupcake had pink frosting and sprinkles."],
["kiss","亲吻","qīnwěn","el beso","When you touch someone with your lips to show love.","Mommy gave me a goodnight kiss on the forehead."],
["ribbon","丝带","sīdài","la cinta","A long, thin strip of pretty cloth for tying bows.","She tied a yellow ribbon in her hair."],
["teddy bear","泰迪熊","tàidíxióng","el osito de peluche","A soft stuffed bear to hug.","I sleep with my teddy bear every night."],
["letter","信","xìn","la carta","A message you write on paper and send to someone.","We mailed a letter to Grandma."],
["mailbox","信箱","xìnxiāng","el buzón","A box where letters are dropped off and picked up.","The mailbox was full of cards today."],
["chocolate","巧克力","qiǎokèlì","el chocolate","A sweet brown treat made from cocoa beans.","The chocolate melted all over my fingers."],
["love","爱","ài","el amor","The warm, happy feeling you have for the people you care about.","Our family is full of love."],
["hand","手","shǒu","la mano","The part at the end of your arm with five fingers.","I held Daddy's hand when we crossed the street."],
["smile","微笑","wēixiào","la sonrisa","When the corners of your mouth go up because you are happy.","Her smile was as bright as the sun."],
["puppy","小狗","xiǎogǒu","el cachorro","A baby dog.","The puppy chased its own tail around and around."],
["kitten","小猫","xiǎomāo","el gatito","A baby cat.","The kitten fell asleep in a sunny spot."],
["bubble","泡泡","pàopao","la burbuja","A floating ball of soapy water that pops.","We blew bubbles that floated over the fence."],
["crayon","蜡笔","làbǐ","el crayón","A stick of colored wax that you draw with.","She colored the sky with a purple crayon."],
["glitter","亮片","liàngpiàn","la purpurina","Tiny shiny sparkles that stick to everything.","There was glitter all over the kitchen table."],
["sticker","贴纸","tiēzhǐ","la pegatina","A picture with glue on the back so it sticks.","She put a star sticker right on her hand."],
["coin","硬币","yìngbì","la moneda","A small, round piece of metal money.","I dropped a coin into my piggy bank."],
["piggy bank","存钱罐","cúnqiánguàn","la alcancía","A little jar or pig where you save your money.","My piggy bank jingles when I shake it."],
["tooth","牙齿","yáchǐ","el diente","One of the hard white things in your mouth you chew with.","My tooth is wiggly and almost ready to come out."],
["toothbrush","牙刷","yáshuā","el cepillo de dientes","A little brush that cleans your teeth.","I use my toothbrush every morning and every night."],
["mouse","老鼠","lǎoshǔ","el ratón","A tiny animal with big ears and a long tail.","The mouse nibbled a crumb of cheese."],
["cheese","奶酪","nǎilào","el queso","A food made from milk, often yellow or white.","He put a slice of cheese on his cracker."],
["frog","青蛙","qīngwā","la rana","A green animal that jumps and says ribbit.","The frog leaped from one lily pad to another."]
],
// ── March: wind, rain, and the first signs of spring (31) ──
[
["wind","风","fēng","el viento","Moving air that you cannot see but can feel.","The wind blew all the leaves into one big pile."],
["kite","风筝","fēngzheng","la cometa","A toy on a string that flies when the wind pushes it.","The kite went up so high it looked like a dot."],
["cloud","云","yún","la nube","White fluffy shapes that float in the sky and hold rain.","That cloud looks exactly like an elephant."],
["umbrella","雨伞","yǔsǎn","el paraguas","A cover you hold over your head to stay dry in the rain.","Our umbrella flipped inside out in the wind."],
["puddle","水坑","shuǐkēng","el charco","A little pool of rainwater on the ground.","She jumped in every puddle on the way home."],
["raindrop","雨滴","yǔdī","la gota de lluvia","One tiny drop of rain falling from the sky.","Raindrops raced each other down the window."],
["rainbow","彩虹","cǎihóng","el arcoíris","A curve of colors in the sky after it rains.","A rainbow stretched over the whole neighborhood."],
["worm","蚯蚓","qiūyǐn","la lombriz","A long, wiggly animal that lives in the dirt.","After the rain, a worm wiggled across the sidewalk."],
["seed","种子","zhǒngzi","la semilla","A tiny thing you put in dirt so a plant can grow.","We planted one seed and waited two whole weeks."],
["sprout","嫩芽","nènyá","el brote","A tiny new plant that is just starting to grow.","A green sprout poked up out of the dirt."],
["clover","三叶草","sānyècǎo","el trébol","A little green plant whose leaves grow in groups of three.","She searched the grass for a four-leaf clover."],
["gold","金子","jīnzi","el oro","A shiny yellow metal that is worth a lot.","The treasure chest was full of gold."],
["boat","船","chuán","el barco","Something that floats and carries people across water.","We sailed our paper boat in the puddle."],
["circle","圆圈","yuánquān","el círculo","A perfectly round shape with no corners.","We sat in a circle and sang songs."],
["lamb","小羊","xiǎoyáng","el cordero","A baby sheep.","The lamb followed the farmer everywhere."],
["duck","鸭子","yāzi","el pato","A bird that swims and says quack.","The ducks lined up and waddled to the pond."],
["green","绿色","lǜsè","el verde","The color of grass and leaves.","Everything in the garden was bright green."],
["pond","池塘","chítáng","el estanque","A small, calm lake.","Tadpoles were swimming all over the pond."],
["tadpole","蝌蚪","kēdǒu","el renacuajo","A baby frog that swims and has a tail.","The tadpole grew legs and turned into a frog."],
["spring","春天","chūntiān","la primavera","The season when flowers bloom and baby animals are born.","In spring, the trees get their leaves back."],
["bird","鸟","niǎo","el pájaro","An animal with feathers and wings.","A little bird sang outside my window."],
["nest","鸟巢","niǎocháo","el nido","A little bowl of sticks where birds keep their eggs.","Three blue eggs were sitting in the nest."],
["egg","蛋","dàn","el huevo","An oval shell that a baby bird grows inside.","The egg cracked and out came a fuzzy chick."],
["chick","小鸡","xiǎojī","el pollito","A baby chicken.","The chick said peep, peep, peep."],
["bunny","小兔子","xiǎo tùzi","el conejito","A small, fluffy rabbit with long ears.","The bunny hopped all around the garden."],
["carrot","胡萝卜","húluóbo","la zanahoria","An orange vegetable that grows under the ground.","The bunny munched a crunchy carrot."],
["mud","泥巴","níba","el barro","Wet, squishy dirt.","His boots were covered in mud."],
["feather","羽毛","yǔmáo","la pluma","The soft, light thing that covers a bird and helps it fly.","I found a blue feather under the tree."],
["bee","蜜蜂","mìfēng","la abeja","A buzzing bug that makes honey.","A bee buzzed from flower to flower."],
["honey","蜂蜜","fēngmì","la miel","Sweet, sticky gold food that bees make.","He put honey on his toast and licked his fingers."],
["petal","花瓣","huābàn","el pétalo","One of the soft, colorful parts of a flower.","Pink petals fell like snow from the tree."]
],
// ── April: flowers, bugs, and spring storms (30) ──
[
["joke","笑话","xiàohua","el chiste","Something funny you say to make people laugh.","Daddy told a joke and I laughed so hard."],
["flower","花","huā","la flor","The colorful part of a plant that often smells nice.","She picked a yellow flower for Mommy."],
["tulip","郁金香","yùjīnxiāng","el tulipán","A cup-shaped flower that blooms in spring.","Red and yellow tulips lined the sidewalk."],
["ladybug","瓢虫","piáochóng","la mariquita","A little red bug with black spots.","A ladybug crawled up my finger."],
["caterpillar","毛毛虫","máomaochóng","la oruga","A fuzzy crawling bug that turns into a butterfly.","The caterpillar munched a hole in the leaf."],
["butterfly","蝴蝶","húdié","la mariposa","A bug with big colorful wings that used to be a caterpillar.","A butterfly landed right on her finger."],
["snail","蜗牛","wōniú","el caracol","A slow little animal that carries a spiral shell.","The snail left a shiny trail on the sidewalk."],
["ant","蚂蚁","mǎyǐ","la hormiga","A tiny, strong bug that lives in a big group.","A line of ants carried crumbs back home."],
["garden","花园","huāyuán","el jardín","A patch of ground where people grow flowers or food.","There were tomatoes and sunflowers in the garden."],
["watering can","喷壶","pēnhú","la regadera","A can with a spout for giving plants a drink.","She filled the watering can and watered the flowers."],
["root","根","gēn","la raíz","The part of a plant that grows down under the ground.","The old tree root pushed the sidewalk up."],
["tree","树","shù","el árbol","A tall plant with a wooden trunk and branches.","We climbed the tree to see the whole yard."],
["leaf","叶子","yèzi","la hoja","The flat green part that grows on a plant.","A leaf floated down and landed on my head."],
["thunder","雷","léi","el trueno","The loud booming sound that comes after lightning.","Thunder shook the windows, but we stayed cozy."],
["lightning","闪电","shǎndiàn","el relámpago","A bright flash of electricity in a stormy sky.","Lightning lit up the whole sky for a second."],
["storm","暴风雨","bàofēngyǔ","la tormenta","Strong wind and heavy rain, sometimes with thunder.","We watched the storm from the couch."],
["raincoat","雨衣","yǔyī","el impermeable","A jacket that keeps the rain off you.","Her yellow raincoat kept her dry."],
["turtle","乌龟","wūguī","la tortuga","An animal that carries its hard shell house on its back.","The turtle pulled its head inside when we got close."],
["fish","鱼","yú","el pez","An animal that lives and breathes underwater.","A little orange fish swam around the tank."],
["hill","小山","xiǎoshān","la colina","Land that goes up, smaller than a mountain.","We rolled all the way down the grassy hill."],
["bottle","瓶子","píngzi","la botella","A container that holds a drink.","We put the empty bottle in the recycling bin."],
["Earth","地球","dìqiú","la Tierra","The planet we live on.","Earth looks blue and green from space."],
["sun","太阳","tàiyáng","el sol","The big bright star that lights up our day.","The sun peeked out from behind the clouds."],
["shadow","影子","yǐngzi","la sombra","The dark shape you make when you stand in the sun.","My shadow got longer as the sun went down."],
["picnic","野餐","yěcān","el pícnic","A meal you eat outside on a blanket.","We had a picnic under the big oak tree."],
["basket","篮子","lánzi","la canasta","A container woven from sticks or straw.","We carried the sandwiches in a basket."],
["sandwich","三明治","sānmíngzhì","el sándwich","Food with something yummy between two slices of bread.","She cut her sandwich into triangles."],
["grass","草","cǎo","el pasto","The thin green plants that cover the ground in a yard.","The grass tickled our bare feet."],
["dandelion","蒲公英","púgōngyīng","el diente de león","A yellow flower that turns into fluffy seeds you can blow.","She made a wish and blew the dandelion."],
["wish","愿望","yuànwàng","el deseo","Something you hope will happen.","I closed my eyes and made a wish."]
],
// ── May: farm, fruit, and the zoo (31) ──
[
["farm","农场","nóngchǎng","la granja","A place where people grow food and raise animals.","We fed the goats at the farm."],
["cow","奶牛","nǎiniú","la vaca","A big farm animal that gives us milk.","The cow said moo and swished her tail."],
["milk","牛奶","niúnǎi","la leche","A white drink that comes from cows.","He had a milk mustache after breakfast."],
["horse","马","mǎ","el caballo","A big, strong animal people can ride.","The horse galloped across the field."],
["guitar","吉他","jítā","la guitarra","An instrument with strings that you strum to make music.","Grandpa played a song on his guitar."],
["pig","猪","zhū","el cerdo","A pink farm animal with a curly tail.","The pig rolled happily in the mud."],
["goat","山羊","shānyáng","la cabra","A farm animal with little horns that loves to climb.","The goat tried to eat my shoelace."],
["barn","谷仓","gǔcāng","el granero","A big building on a farm where animals sleep.","The red barn was full of hay."],
["hay","干草","gāncǎo","el heno","Dry grass that farm animals eat.","We jumped into a big pile of hay."],
["tractor","拖拉机","tuōlājī","el tractor","A strong machine that pulls things on a farm.","The tractor rumbled across the field."],
["strawberry","草莓","cǎoméi","la fresa","A red, sweet fruit with tiny seeds on the outside.","We picked a whole bucket of strawberries."],
["bucket","水桶","shuǐtǒng","la cubeta","A round container with a handle for carrying things.","She filled her bucket with water."],
["hose","水管","shuǐguǎn","la manguera","A long tube that sprays water.","Daddy sprayed us with the garden hose."],
["sprinkler","洒水器","sǎshuǐqì","el aspersor","A thing that sprays water all over the grass.","We ran through the sprinkler, giggling."],
["lemon","柠檬","níngméng","el limón","A sour yellow fruit.","She made a funny face when she bit the lemon."],
["lemonade","柠檬水","níngméngshuǐ","la limonada","A sweet and sour drink made from lemons.","We sold lemonade on the corner."],
["cherry","樱桃","yīngtáo","la cereza","A small, round, red fruit with a pit inside.","She hung two cherries over her ear like earrings."],
["apple","苹果","píngguǒ","la manzana","A crunchy, round fruit that grows on trees.","I packed an apple in my lunch."],
["banana","香蕉","xiāngjiāo","el plátano","A long yellow fruit that you peel.","The monkey peeled a banana."],
["monkey","猴子","hóuzi","el mono","A playful animal that swings from trees.","The monkey swung from branch to branch."],
["zoo","动物园","dòngwùyuán","el zoológico","A place where you can visit animals from all over the world.","At the zoo we saw a lion taking a nap."],
["lion","狮子","shīzi","el león","A big wild cat with a fluffy mane that roars.","The lion let out a giant roar."],
["giraffe","长颈鹿","chángjǐnglù","la jirafa","The tallest animal, with a super long neck.","The giraffe ate leaves from the top of the tree."],
["zebra","斑马","bānmǎ","la cebra","A horse-like animal with black and white stripes.","No two zebras have the same stripes."],
["elephant","大象","dàxiàng","el elefante","A huge gray animal with a long nose it uses like a hand.","The elephant picked up a whole watermelon with its trunk."],
["parrot","鹦鹉","yīngwǔ","el loro","A colorful bird that can copy words.","The parrot said hello back to me."],
["flamingo","火烈鸟","huǒlièniǎo","el flamenco","A pink bird that stands on one leg.","The flamingo balanced on one skinny leg."],
["kangaroo","袋鼠","dàishǔ","el canguro","An animal that hops and carries its baby in a pouch.","The baby kangaroo peeked out of the pouch."],
["koala","考拉","kǎolā","el koala","A fuzzy gray animal that hugs trees and sleeps a lot.","The koala hugged the tree and fell asleep."],
["panda","熊猫","xióngmāo","el panda","A black and white bear from China that eats bamboo.","The panda munched on bamboo all day."],
["bamboo","竹子","zhúzi","el bambú","A tall, hollow plant that grows super fast.","The bamboo grew taller than our house."]
],
// ── June: summer, the beach, and camping (30) ──
[
["summer","夏天","xiàtiān","el verano","The hottest season, when school is out.","In summer we go swimming almost every day."],
["beach","海滩","hǎitān","la playa","Sandy land right next to the ocean.","We built a sandcastle at the beach."],
["sand","沙子","shāzi","la arena","Tiny grains of rock that you find at the beach.","The sand was warm under our toes."],
["wave","海浪","hǎilàng","la ola","Water that rolls and crashes onto the shore.","A big wave knocked over my sandcastle."],
["shell","贝壳","bèiké","la concha","The hard, curvy home a sea animal leaves on the beach.","She held the shell to her ear to hear the ocean."],
["crab","螃蟹","pángxiè","el cangrejo","A sea animal that walks sideways and has claws.","A little crab scuttled into its hole."],
["starfish","海星","hǎixīng","la estrella de mar","A sea animal shaped like a star.","We found a starfish in the tide pool."],
["ocean","海洋","hǎiyáng","el océano","The enormous body of salty water that covers most of Earth.","The ocean was so big we could not see the other side."],
["whale","鲸鱼","jīngyú","la ballena","The biggest animal in the ocean, bigger than a school bus.","The whale came up for air and made a huge splash."],
["dolphin","海豚","hǎitún","el delfín","A smart, playful sea animal that jumps out of the water.","Dolphins leaped next to our boat."],
["octopus","章鱼","zhāngyú","el pulpo","A sea animal with eight long arms.","The octopus squirted ink and swam away."],
["shark","鲨鱼","shāyú","el tiburón","A big fish with lots of sharp teeth.","The shark swam in slow, quiet circles."],
["jellyfish","水母","shuǐmǔ","la medusa","A see-through sea animal that wobbles like jelly.","The jellyfish glowed in the dark water."],
["island","岛","dǎo","la isla","Land with water all the way around it.","We rowed to the little island in the middle of the lake."],
["lighthouse","灯塔","dēngtǎ","el faro","A tall tower by the sea with a light that warns boats.","The lighthouse swept its beam across the dark water."],
["anchor","锚","máo","el ancla","A heavy hook a boat drops so it stops floating away.","They dropped the anchor and stopped for lunch."],
["sailboat","帆船","fānchuán","el velero","A boat pushed along by the wind in its sail.","The sailboat glided across the lake."],
["sunglasses","太阳镜","tàiyángjìng","las gafas de sol","Dark glasses that protect your eyes from the bright sun.","Daddy looked so cool in his sunglasses."],
["sunscreen","防晒霜","fángshàishuāng","el protector solar","A lotion that keeps the sun from burning your skin.","Mommy put sunscreen on my nose."],
["ice cream","冰淇淋","bīngqílín","el helado","A cold, sweet, creamy treat.","My ice cream melted down my hand."],
["popsicle","冰棒","bīngbàng","la paleta de hielo","Frozen juice on a stick.","Her tongue turned blue from the popsicle."],
["watermelon","西瓜","xīguā","la sandía","A big green fruit that is red and juicy inside.","We had a seed-spitting contest with watermelon."],
["fan","风扇","fēngshàn","el ventilador","A machine with spinning blades that blows air.","I sang into the fan to make my voice sound funny."],
["hammock","吊床","diàochuáng","la hamaca","A swinging bed of cloth or rope hung between two trees.","We rocked in the hammock and watched the clouds."],
["tent","帐篷","zhàngpeng","la tienda de campaña","A little house made of cloth that you sleep in outdoors.","We camped in a tent in the backyard."],
["campfire","篝火","gōuhuǒ","la fogata","A fire you make outside when camping.","We told stories around the campfire."],
["marshmallow","棉花糖","miánhuatáng","el malvavisco","A soft, puffy white candy.","My marshmallow caught on fire!"],
["flashlight","手电筒","shǒudiàntǒng","la linterna","A small light you carry that runs on batteries.","We made shadow puppets with a flashlight."],
["firefly","萤火虫","yínghuǒchóng","la luciérnaga","A bug whose tail blinks with light on summer nights.","We caught one firefly in a jar and then let it go."],
["cricket","蟋蟀","xīshuài","el grillo","A little jumping bug that chirps at night.","The crickets sang us to sleep."]
],
// ── July: celebrations, adventures, and outer space (31) ──
[
["bicycle","自行车","zìxíngchē","la bicicleta","A ride with two wheels and pedals.","She rode her bicycle without training wheels!"],
["helmet","头盔","tóukuī","el casco","A hard hat that protects your head.","Always wear your helmet when you ride."],
["flag","旗子","qízi","la bandera","A piece of cloth with colors and shapes that stands for a place.","The flag waved in the breeze."],
["fireworks","烟花","yānhuā","los fuegos artificiales","Colorful sparkles that burst in the night sky.","The fireworks went boom and lit up the sky."],
["parade","游行","yóuxíng","el desfile","A line of people, music, and floats marching down the street.","We waved at the parade from the sidewalk."],
["drum","鼓","gǔ","el tambor","A round thing you hit to make a deep booming sound.","He banged the drum until everybody was dancing."],
["trumpet","小号","xiǎohào","la trompeta","A shiny instrument you blow into to make loud music.","The trumpet played a loud, happy song."],
["balloon","气球","qìqiú","el globo","A stretchy bag that floats when you fill it with special air.","The balloon slipped out of her hand and floated away."],
["lake","湖","hú","el lago","A big body of water with land all around it.","We skipped rocks across the lake."],
["canoe","独木舟","dúmùzhōu","la canoa","A long, narrow boat you paddle.","We paddled the canoe to the other side."],
["paddle","桨","jiǎng","el remo","A stick with a flat end for moving a boat through water.","She dipped her paddle into the water."],
["river","河","hé","el río","Water that keeps moving in one long line across the land.","We threw sticks in the river and watched them float away."],
["waterfall","瀑布","pùbù","la cascada","Water that falls down from a high place.","The waterfall roared and splashed."],
["rock","岩石","yánshí","la roca","A big, hard piece of stone.","We climbed onto the big rock by the river."],
["stone","石头","shítou","la piedra","A hard piece of rock you can pick up in your hand.","He skipped a flat stone across the pond four times."],
["bridge","桥","qiáo","el puente","A road built over water so you can get to the other side.","We drove over the bridge and waved at the boats below."],
["path","小路","xiǎolù","el sendero","A narrow trail where people have walked again and again.","The path curved behind the trees and disappeared."],
["map","地图","dìtú","el mapa","A drawing that shows where places are and how to get there.","We spread the map out on the floor."],
["compass","指南针","zhǐnánzhēn","la brújula","A little tool with a needle that always points north.","We used a compass to find our way back to camp."],
["moon","月亮","yuèliang","la luna","The big light that comes out in the sky at night.","The moon followed us all the way home in the car."],
["astronaut","宇航员","yǔhángyuán","el astronauta","A person who travels into space.","The astronaut floated inside the spaceship."],
["rocket","火箭","huǒjiàn","el cohete","A tall machine that shoots straight up into space.","The rocket left a long white line across the sky."],
["planet","行星","xíngxīng","el planeta","A giant round world that circles around a star.","Earth is the planet we live on."],
["star","星星","xīngxing","la estrella","A tiny bright light far away in the night sky.","We counted stars until we lost track."],
["comet","彗星","huìxīng","el cometa","A ball of ice and dust that zooms through space with a glowing tail.","The comet streaked across the night sky."],
["alien","外星人","wàixīngrén","el extraterrestre","A make-believe creature from another planet.","In my story, a friendly alien came over for dinner."],
["telescope","望远镜","wàngyuǎnjìng","el telescopio","A long tube you look through to see faraway things up close.","Through the telescope we could see the craters on the moon."],
["galaxy","星系","xīngxì","la galaxia","A giant group of billions of stars.","Our sun is just one star in a huge galaxy."],
["robot","机器人","jīqìrén","el robot","A machine that can move and do jobs by itself.","The robot vacuum bumped into my toy."],
["sunflower","向日葵","xiàngrìkuí","el girasol","A tall flower with a big yellow face that follows the sun.","The sunflower grew taller than Daddy."],
["treehouse","树屋","shùwū","la casa del árbol","A little house built up in a tree.","We read books up in the treehouse."]
],
// ── August: desert, dinosaurs, wild animals, and back to school (31) ──
[
["desert","沙漠","shāmò","el desierto","A huge dry place made of sand where almost no rain falls.","Nothing but sand and sky in every direction of the desert."],
["cactus","仙人掌","xiānrénzhǎng","el cactus","A prickly plant that grows in the desert.","Don't touch the cactus, it's spiky!"],
["camel","骆驼","luòtuo","el camello","A desert animal with a hump on its back.","The camel walked for days without water."],
["lizard","蜥蜴","xīyì","la lagartija","A small animal with scales and a long tail.","A lizard sunbathed on the warm rock."],
["snake","蛇","shé","la serpiente","A long animal with no legs that slithers.","The snake flicked out its tongue."],
["volcano","火山","huǒshān","el volcán","A mountain that can open up and pour out hot melted rock.","The volcano had not erupted in a hundred years."],
["dinosaur","恐龙","kǒnglóng","el dinosaurio","A giant animal that lived a very, very long time ago.","The dinosaur bones were as big as a car."],
["fossil","化石","huàshí","el fósil","A very old bone or shell that turned into stone.","We found a fossil of a tiny seashell."],
["cave","山洞","shāndòng","la cueva","A big hole in a rock or hill that you can walk inside.","The cave was cold and echoed when we shouted."],
["bat","蝙蝠","biānfú","el murciélago","A furry animal with wings that flies at night.","Bats hung upside down in the cave."],
["tiger","老虎","lǎohǔ","el tigre","A big orange cat with black stripes.","The tiger crept quietly through the grass."],
["cheetah","猎豹","lièbào","el guepardo","The fastest animal on land, covered in spots.","The cheetah zoomed across the field."],
["rhinoceros","犀牛","xīniú","el rinoceronte","A huge animal with a horn on its nose.","The rhinoceros splashed in the mud."],
["hippo","河马","hémǎ","el hipopótamo","A giant animal that loves to sit in the water.","The hippo yawned a gigantic yawn."],
["crocodile","鳄鱼","èyú","el cocodrilo","A big reptile with lots of teeth that lives in rivers.","The crocodile floated like a log."],
["peacock","孔雀","kǒngquè","el pavo real","A bird with a huge, colorful fan of tail feathers.","The peacock spread its beautiful tail."],
["backpack","书包","shūbāo","la mochila","A bag you carry on your back.","She packed her backpack for the first day of school."],
["pencil","铅笔","qiānbǐ","el lápiz","A stick you write and draw with.","I sharpened my pencil to a tiny point."],
["eraser","橡皮","xiàngpí","el borrador","A rubbery thing that rubs out pencil marks.","I used my eraser to fix my drawing."],
["scissors","剪刀","jiǎndāo","las tijeras","A tool with two blades for cutting paper.","We cut out paper snowflakes with scissors."],
["glue","胶水","jiāoshuǐ","el pegamento","Sticky stuff that holds things together.","The glue made my fingers sticky."],
["teacher","老师","lǎoshī","el maestro","A person who helps you learn.","My teacher read us a story about a bear."],
["book","书","shū","el libro","Pages with words and pictures, held together.","This is my favorite book in the whole world."],
["school bus","校车","xiàochē","el autobús escolar","A big yellow bus that takes kids to school.","We waved at the school bus as it drove by."],
["lunchbox","午餐盒","wǔcānhé","la lonchera","A box that holds your lunch.","She found a note from Mommy in her lunchbox."],
["paint","颜料","yánliào","la pintura","Colorful liquid you brush onto paper.","We used purple paint to make a dragon."],
["paintbrush","画笔","huàbǐ","el pincel","A brush for painting.","I washed my paintbrush in a cup of water."],
["alphabet","字母表","zìmǔbiǎo","el abecedario","All the letters, from A to Z.","We sang the alphabet song together."],
["number","数字","shùzì","el número","A symbol that tells how many, like 1, 2, 3.","Five is my favorite number."],
["clock","时钟","shízhōng","el reloj","A thing that tells you what time it is.","The clock said it was time for bed."],
["globe","地球仪","dìqiúyí","el globo terráqueo","A round model of the Earth.","We spun the globe and pointed to China."]
],
// ── September: harvest, castles, and make-believe (30) ──
[
["orchard","果园","guǒyuán","el huerto","A place where lots of fruit trees grow.","We picked apples at the orchard."],
["pear","梨","lí","la pera","A sweet, juicy fruit that is round at the bottom.","The pear was so juicy it dripped down my chin."],
["grape","葡萄","pútao","la uva","A small, round fruit that grows in bunches.","She ate the grapes one by one."],
["corn","玉米","yùmǐ","el maíz","A vegetable with rows of yellow kernels on a cob.","We ate corn on the cob with butter."],
["scarecrow","稻草人","dàocǎorén","el espantapájaros","A straw person in a field that scares away birds.","The scarecrow wore an old floppy hat."],
["crow","乌鸦","wūyā","el cuervo","A big, shiny black bird that says caw.","A crow sat right on the scarecrow's head."],
["squirrel","松鼠","sōngshǔ","la ardilla","A furry animal with a bushy tail that collects nuts.","The squirrel buried an acorn in our yard."],
["acorn","橡子","xiàngzǐ","la bellota","A little nut that grows on an oak tree.","She filled her pocket with acorns."],
["hedgehog","刺猬","cìwei","el erizo","A small animal covered in prickly spikes.","The hedgehog rolled into a spiky ball."],
["mushroom","蘑菇","mógu","el hongo","Something that grows from the ground shaped like a little umbrella.","A mushroom popped up after the rain."],
["lantern","灯笼","dēnglong","el farol","A little light you can carry, with paper or glass around it.","She carried a red lantern down the dark path."],
["puzzle","拼图","pīntú","el rompecabezas","Pieces you fit together to make a picture.","We finished a puzzle with 100 pieces."],
["block","积木","jīmù","el bloque","A toy piece you stack to build things.","We built the tallest tower out of blocks."],
["castle","城堡","chéngbǎo","el castillo","A giant stone house with towers and thick walls.","The castle had a bridge that pulled up."],
["crown","王冠","wángguān","la corona","A fancy hat that a king or queen wears.","She wore a paper crown all day."],
["dragon","龙","lóng","el dragón","A make-believe animal with wings that can breathe fire.","In the story, the dragon was afraid of mice."],
["knight","骑士","qíshì","el caballero","A brave person in armor who rides a horse.","The knight and the dragon became best friends."],
["princess","公主","gōngzhǔ","la princesa","The daughter of a king or queen.","The princess climbed down the tower all by herself."],
["wand","魔杖","mózhàng","la varita mágica","A magic stick for casting spells.","She waved her wand and turned me into a frog."],
["magic","魔法","mófǎ","la magia","Something that seems to happen in an impossible way.","The magician did a magic trick with a coin."],
["treasure","宝藏","bǎozàng","el tesoro","A pile of gold or jewels that somebody hid long ago.","The map said the treasure was buried under the big rock."],
["key","钥匙","yàoshi","la llave","A small metal thing that opens a lock.","I could not find the key, so we knocked instead."],
["autumn","秋天","qiūtiān","el otoño","The season when leaves change color and fall.","In autumn, the leaves turn orange and red."],
["mirror","镜子","jìngzi","el espejo","Smooth glass that shows you a picture of yourself.","She made silly faces at herself in the mirror."],
["puppet","木偶","mù'ǒu","el títere","A little person or animal you move with your hand or strings.","He made the puppet talk in a squeaky voice."],
["bell","铃铛","língdang","la campana","A metal cup that rings when something swings inside it.","The bell rang and everyone ran outside."],
["story","故事","gùshi","el cuento","Words that tell about something that happened, real or made up.","She asked for one more story before bed."],
["library","图书馆","túshūguǎn","la biblioteca","A place full of books you can borrow.","We checked out five books from the library."],
["piano","钢琴","gāngqín","el piano","An instrument with black and white keys.","She played a song on the piano."],
["song","歌","gē","la canción","Words and music that you sing.","We made up a song about pancakes."]
],
// ── October: fall leaves and Halloween (31) ──
[
["pumpkin","南瓜","nánguā","la calabaza","A big, round, orange vegetable.","We picked the biggest pumpkin in the patch."],
["maple leaf","枫叶","fēngyè","la hoja de arce","A leaf with pointy tips that turns red in the fall.","A red maple leaf floated down to the ground."],
["rake","耙子","pázi","el rastrillo","A tool with long teeth for gathering leaves.","Daddy raked the leaves into one big pile."],
["wagon","小推车","xiǎotuīchē","el carrito","A little cart with wheels that you pull by a handle.","I pulled my teddy bear around in the wagon."],
["pie","派","pài","la tarta","A baked dessert with a crust and a sweet filling.","The whole house smelled like apple pie."],
["cinnamon","肉桂","ròuguì","la canela","A brown spice that smells warm and sweet.","We sprinkled cinnamon on our oatmeal."],
["jacket","夹克","jiākè","la chaqueta","A coat you wear when it is a little chilly.","Zip up your jacket, it's windy!"],
["goose","鹅","é","el ganso","A big bird that honks and flies south in the fall.","The geese flew by in a big V shape."],
["south","南方","nánfāng","el sur","The direction at the bottom of a map.","Many birds fly south for the winter."],
["spider","蜘蛛","zhīzhū","la araña","A small animal with eight legs that spins sticky webs.","A spider built a web across the whole doorway."],
["web","蜘蛛网","zhīzhūwǎng","la telaraña","The sticky net a spider spins.","Dew made the spider web sparkle."],
["raccoon","浣熊","huànxióng","el mapache","An animal with a striped tail and a black mask around its eyes.","A raccoon peeked into our trash can."],
["skunk","臭鼬","chòuyòu","el zorrillo","A black and white animal that can make a big stink.","We tiptoed away from the skunk."],
["skeleton","骨架","gǔjià","el esqueleto","All the bones inside your body, put together.","The skeleton at the museum was a T. rex."],
["bone","骨头","gǔtou","el hueso","One of the hard parts inside your body that holds you up.","The dog buried a bone in the yard."],
["costume","戏服","xìfú","el disfraz","Special clothes you wear to pretend to be someone else.","She picked a butterfly costume this year."],
["mask","面具","miànjù","la máscara","A cover for your face, like for a costume.","He wore a tiger mask and roared."],
["ghost","幽灵","yōulíng","el fantasma","A make-believe spooky spirit, like a floating sheet.","The friendly ghost said boo and giggled."],
["witch","女巫","nǚwū","la bruja","A make-believe person who does magic, often with a pointy hat.","The witch flew by on her broom."],
["broom","扫帚","sàozhou","la escoba","A brush with a long handle for sweeping.","She swept the leaves off the porch with a broom."],
["pot","锅","guō","la olla","A deep pan for cooking soup.","Mommy stirred the big pot of soup."],
["black cat","黑猫","hēimāo","el gato negro","A cat with black fur.","A black cat curled up on our porch."],
["moonlight","月光","yuèguāng","la luz de la luna","The soft light that comes from the moon.","The moonlight made the yard glow silver."],
["whisper","悄悄话","qiāoqiāohuà","el susurro","Talking very, very quietly.","She told me a secret in a tiny whisper."],
["candy","糖果","tángguǒ","el dulce","A sweet treat.","We traded candy after trick-or-treating."],
["lollipop","棒棒糖","bàngbàngtáng","la paleta","A hard candy on a stick.","Her lollipop was as big as her face."],
["doorbell","门铃","ménlíng","el timbre","A button by the door that rings when you press it.","Ding-dong! The doorbell rang."],
["porch","门廊","ménláng","el porche","A covered spot right outside the front door.","We sat on the porch and waited for trick-or-treaters."],
["haunted house","鬼屋","guǐwū","la casa embrujada","A pretend house full of spooky surprises.","The haunted house had cobwebs everywhere."],
["wolf","狼","láng","el lobo","A wild animal like a big dog that howls at the moon.","The wolf howled at the big round moon."],
["jack-o'-lantern","南瓜灯","nánguādēng","la calabaza de Halloween","A pumpkin with a carved face and a light inside.","Our jack-o'-lantern had a big toothy grin."]
],
// ── November: harvest, food, and family (30) ──
[
["harvest","收获","shōuhuò","la cosecha","When farmers gather the food they grew.","The harvest filled the barn with corn and squash."],
["turkey","火鸡","huǒjī","el pavo","A big bird with a fan of feathers that gobbles.","The turkey said gobble, gobble."],
["feast","盛宴","shèngyàn","el banquete","A big, special meal with lots of food.","Everyone came over for a giant feast."],
["bread","面包","miànbāo","el pan","A food made from flour that you bake.","Warm bread with butter is my favorite."],
["potato","土豆","tǔdòu","la papa","A lumpy brown vegetable that grows underground.","We mashed the potatoes with lots of butter."],
["cranberry","蔓越莓","mànyuèméi","el arándano rojo","A small, sour red berry.","The cranberry sauce wiggled on the plate."],
["blueberry","蓝莓","lánméi","el arándano azul","A small, round, blue fruit.","Blueberries turned my tongue purple."],
["oven","烤箱","kǎoxiāng","el horno","A hot box in the kitchen for baking food.","The cookies are baking in the oven."],
["cookie","饼干","bǐnggān","la galleta","A small, sweet baked treat.","Mommy makes the best cookies in the whole world."],
["recipe","食谱","shípǔ","la receta","Directions that tell you how to cook something.","We followed Grandma's recipe for bread."],
["spoon","勺子","sháozi","la cuchara","A tool with a little bowl on the end for eating soup.","I stirred my cocoa with a spoon."],
["fork","叉子","chāzi","el tenedor","A tool with pointy prongs for eating food.","She twirled spaghetti on her fork."],
["noodles","面条","miàntiáo","los fideos","Long, thin strips of dough that you cook in water.","We slurped our noodles super loud."],
["rice","米饭","mǐfàn","el arroz","Tiny white grains that you cook and eat.","We ate chicken and rice for dinner."],
["chopsticks","筷子","kuàizi","los palillos","Two thin sticks used for eating.","I can pick up a peanut with my chopsticks."],
["tea","茶","chá","el té","A warm drink made from leaves.","Grandma and I had a pretend tea party."],
["teapot","茶壶","cháhú","la tetera","A pot with a spout for pouring tea.","The teapot whistled on the stove."],
["grandma","奶奶","nǎinai","la abuela","Your mom's or dad's mom.","Grandma always has candy in her purse."],
["grandpa","爷爷","yéye","el abuelo","Your mom's or dad's dad.","Grandpa taught me how to whistle."],
["family","家庭","jiātíng","la familia","The people who love you and take care of you.","Our family holds hands before dinner."],
["home","家","jiā","el hogar","The place where you live with your family.","There's no place like home."],
["house","房子","fángzi","la casa","A building where people live.","We drew our house with smoke curling from the roof."],
["window","窗户","chuānghu","la ventana","Glass in a wall that lets the light in.","I watched the rain from the window."],
["door","门","mén","la puerta","The thing you open to go in or out of a room.","Knock, knock! Who's at the door?"],
["roof","屋顶","wūdǐng","el techo","The top of a house that keeps the rain out.","A bird landed on our roof."],
["pillow","枕头","zhěntou","la almohada","A soft cushion for your head when you sleep.","We had a giant pillow fight."],
["bathtub","浴缸","yùgāng","la bañera","A big tub you fill with water to get clean.","I made a bubble beard in the bathtub."],
["soap","肥皂","féizào","el jabón","Something that makes bubbles and gets you clean.","The soap slipped right out of my hands."],
["towel","毛巾","máojīn","la toalla","A soft cloth for drying off.","I wrapped up in a warm towel after my bath."],
["dream","梦","mèng","el sueño","The pictures and stories in your head while you are asleep.","In my dream, I could breathe underwater."]
],
// ── December: winter holidays and a new year coming (31) ──
[
["present","礼物","lǐwù","el regalo","Something special you give to someone.","I wrapped a present for my best friend."],
["bow","蝴蝶结","húdiéjié","el moño","A pretty knot tied with ribbon.","She put a big bow on top of the box."],
["wrapping paper","包装纸","bāozhuāngzhǐ","el papel de regalo","Colorful paper for covering presents.","The cat played with the wrapping paper."],
["light","灯光","dēngguāng","la luz","Brightness that helps you see.","The twinkly lights made the tree glow."],
["pine tree","松树","sōngshù","el pino","A tree with needles that stays green all winter.","The pine tree smelled fresh and sharp."],
["ornament","装饰品","zhuāngshìpǐn","el adorno","A pretty decoration you hang on a tree.","She hung a shiny ornament on the tree."],
["candle","蜡烛","làzhú","la vela","A stick of wax with a string on top that holds a little flame.","We lit one candle and turned off all the lights."],
["gingerbread","姜饼","jiāngbǐng","el pan de jengibre","A spicy cookie often shaped like a little person.","The gingerbread man had gumdrop buttons."],
["candy cane","拐杖糖","guǎizhàngtáng","el bastón de caramelo","A striped candy shaped like a hook.","She hung a candy cane on the tree."],
["reindeer","驯鹿","xùnlù","el reno","A deer with big antlers that lives where it is snowy.","The reindeer pulled the sleigh through the snow."],
["stocking","圣诞袜","shèngdànwà","la media navideña","A big sock you hang up for holiday treats.","Her stocking was full of oranges and toys."],
["snow","雪","xuě","la nieve","Soft white pieces of frozen water that fall from clouds.","Snow covered the whole front yard overnight."],
["snowball","雪球","xuěqiú","la bola de nieve","A ball you pack together out of snow.","Daddy got hit with a snowball!"],
["elf","小精灵","xiǎo jīnglíng","el duende","A make-believe tiny helper with pointy ears.","The elf helped wrap all the toys."],
["North Pole","北极","běijí","el Polo Norte","The very top of the Earth, where it is always icy.","Polar bears live near the North Pole."],
["angel","天使","tiānshǐ","el ángel","A make-believe helper with wings and a halo.","We put a shiny angel on top of the tree."],
["music","音乐","yīnyuè","la música","Sounds put together to make songs.","We danced to the music in the kitchen."],
["dance","舞蹈","wǔdǎo","el baile","Moving your body to music.","She made up a silly dance."],
["ice","冰","bīng","el hielo","Water that is frozen solid.","The pond turned to ice overnight."],
["quilt","被子","bèizi","el edredón","A thick, warm blanket for your bed.","I snuggled deep under my quilt."],
["winter","冬天","dōngtiān","el invierno","The coldest season of the year.","In winter, the days are short and the nights are long."],
["night","夜晚","yèwǎn","la noche","The dark time when the sun is down.","The stars came out one by one at night."],
["wreath","花环","huāhuán","la corona navideña","A ring of green branches you hang on a door.","We hung a wreath with a red bow on our door."],
["surprise","惊喜","jīngxǐ","la sorpresa","Something you didn't know was going to happen.","Close your eyes, I have a surprise for you!"],
["Christmas","圣诞节","Shèngdàn Jié","la Navidad","A winter holiday with trees, lights, and presents.","On Christmas morning we opened presents in our pajamas."],
["toy","玩具","wánjù","el juguete","Something you play with.","She shared her new toy with her friend."],
["penguin","企鹅","qǐ'é","el pingüino","A black and white bird that swims instead of flying.","The penguin waddled like it was in a hurry."],
["cardinal","红雀","hóngquè","el cardenal","A bright red bird you can see in winter.","A red cardinal sat on the snowy fence."],
["party","派对","pàiduì","la fiesta","When friends get together to celebrate.","We had a pajama party with our cousins."],
["hat","帽子","màozi","el sombrero","Something you wear on your head.","The wind blew my hat right off!"],
["countdown","倒计时","dàojìshí","la cuenta regresiva","Counting backward to zero, like 3, 2, 1!","We shouted the countdown and cheered at midnight."]
]
];

// ── Holidays whose dates move every year ──
// Keyed by "YYYY-MM-DD". Covers 2026–2031; add more years as needed.
WOTD.MOVING = {
  lunarNewYear: { name: "Lunar New Year",
    dates: ["2027-02-06","2028-01-26","2029-02-13","2030-02-03","2031-01-23"],
    words: [
      ["red envelope","红包","hóngbāo","el sobre rojo","A red paper envelope with a gift of money inside for the new year.","Grandma gave me a red envelope for good luck."],
      ["dumpling","饺子","jiǎozi","la empanadilla","A little pocket of dough with a yummy filling inside.","We folded dumplings together in the kitchen."],
      ["firecracker","鞭炮","biānpào","el petardo","A small paper tube that goes pop-pop-pop to celebrate.","The firecrackers popped to welcome the new year."],
      ["lion dance","舞狮","wǔshī","la danza del león","A dance where people inside a big lion costume leap and shake.","The lion dance jumped right up to our table!"],
      ["new year","新年","xīnnián","el año nuevo","The very first day of a brand-new year.","We said Happy New Year in two languages."]
    ]},
  midAutumn: { name: "Mid-Autumn Festival",
    dates: ["2026-09-25","2027-09-15","2028-10-03","2029-09-22","2030-09-12","2031-10-01"],
    words: [
      ["mooncake","月饼","yuèbing","el pastel de luna","A round cake with a sweet filling, shared under the full moon.","We cut the mooncake into pieces for everyone."],
      ["full moon","满月","mǎnyuè","la luna llena","When the moon looks like a big, bright, round circle.","The full moon was so bright we could see our shadows."],
      ["jade rabbit","玉兔","yùtù","el conejo de jade","A make-believe rabbit that lives on the moon in Chinese stories.","Can you find the jade rabbit on the moon?"]
    ]},
  thanksgiving: { name: "Thanksgiving",   // 4th Thursday of November, computed
    words: [
      ["thankful","感恩","gǎn'ēn","agradecido","Feeling happy about the good things and people you have.","I'm thankful for my family and my friends."]
    ]},
  mothersDay: { name: "Mother's Day",     // 2nd Sunday of May, computed
    words: [
      ["mom","妈妈","māma","la mamá","The mom who loves you and takes care of you.","I made my mama breakfast in bed."]
    ]},
  fathersDay: { name: "Father's Day",     // 3rd Sunday of June, computed
    words: [
      ["dad","爸爸","bàba","el papá","The dad who loves you and takes care of you.","My papa can carry me on his shoulders."]
    ]}
};

// ── Activity words: used when today's calendar has one of these ──
WOTD.ACTIVITY = {
  swim: { label: "Swim day word", words: [
    ["pool","游泳池","yóuyǒngchí","la piscina","A big tub of water in the ground for swimming.","We cannonballed into the pool!"],
    ["goggles","泳镜","yǒngjìng","las gafas de natación","Glasses that keep water out of your eyes when you swim.","With my goggles on, I can see underwater."],
    ["splash","水花","shuǐhuā","el chapoteo","When water jumps up and sprays everywhere.","My big jump made a giant splash."],
    ["kickboard","浮板","fúbǎn","la tabla de natación","A foam board you hold on to while you practice kicking.","I held the kickboard and kicked all the way across."],
    ["dive","跳水","tiàoshuǐ","el clavado","Jumping into water headfirst.","She did her very first dive today."],
    ["swimsuit","泳衣","yǒngyī","el traje de baño","Clothes you wear to go swimming.","She wore her rainbow swimsuit to her lesson."],
    ["lifeguard","救生员","jiùshēngyuán","el salvavidas","A person who keeps swimmers safe.","The lifeguard blew her whistle."]
  ]},
  soccer: { label: "Soccer day word", words: [
    ["ball","球","qiú","la pelota","A round toy you kick, throw, or bounce.","She kicked the ball as hard as she could."],
    ["goal","球门","qiúmén","la portería","The net where you try to kick the ball in soccer.","The ball zoomed right into the goal!"],
    ["team","队","duì","el equipo","A group of people who play together.","Our team gave each other high fives."],
    ["whistle","哨子","shàozi","el silbato","A small thing you blow to make a loud, sharp sound.","The coach blew the whistle to start the game."],
    ["coach","教练","jiàoliàn","el entrenador","A person who teaches a team how to play.","Our coach said we played super hard today."],
    ["cleats","足球鞋","zúqiúxié","los zapatos de fútbol","Special shoes with bumps on the bottom for running on grass.","She laced up her cleats for the big game."],
    ["field","球场","qiúchǎng","la cancha","A big grassy place to play games.","We ran all the way across the field."]
  ]},
  basketball: { label: "Basketball day word", words: [
    ["basketball","篮球","lánqiú","el básquetbol","A game where you bounce a ball and throw it into a hoop.","We practiced basketball in the driveway."],
    ["hoop","篮筐","lánkuāng","el aro","The ring with a net that you throw the ball through.","The ball rolled around the hoop and dropped in!"],
    ["sneakers","运动鞋","yùndòngxié","los tenis","Soft shoes for running and playing.","Her new sneakers squeaked on the court."]
  ]},
  birthday: { label: "Party day word", words: [
    ["birthday","生日","shēngrì","el cumpleaños","The day each year when you celebrate being born.","We sang happy birthday really, really loud."],
    ["cake","蛋糕","dàngāo","el pastel","A sweet, soft dessert, often with frosting on top.","The cake had five candles and pink frosting."],
    ["confetti","彩纸屑","cǎizhǐxiè","el confeti","Tiny pieces of colorful paper you throw to celebrate.","Confetti rained down on everybody's heads."],
    ["invitation","邀请卡","yāoqǐngkǎ","la invitación","A card that asks you to come to a party.","I got an invitation to my friend's party!"]
  ]},
  dentist: { label: "Dentist day word", words: [
    ["dentist","牙医","yáyī","el dentista","A doctor who keeps your teeth healthy.","The dentist counted all my teeth."],
    ["floss","牙线","yáxiàn","el hilo dental","A thin string that cleans between your teeth.","I use floss to clean between my teeth."],
    ["cavity","蛀牙","zhùyá","la caries","A tiny hole in a tooth that needs fixing.","Brushing every day keeps cavities away."]
  ]},
  doctor: { label: "Doctor day word", words: [
    ["doctor","医生","yīshēng","el doctor","A person who helps you stay healthy and feel better.","The doctor said I'm growing big and strong."],
    ["stethoscope","听诊器","tīngzhěnqì","el estetoscopio","A tool a doctor uses to listen to your heartbeat.","I heard my own heart through the stethoscope."],
    ["bandage","创可贴","chuāngkětiē","la curita","A sticky strip that covers a small cut.","She put a bandage with stars on my knee."]
  ]}
};

// ── Pick today's word ──
// Priority: moving holiday > activity on today's calendar > the day's own word.
WOTD.pick = function (date, activities) {
  const pad = n => String(n).padStart(2, "0");
  const y = date.getFullYear(), m = date.getMonth(), d = date.getDate();
  const iso = y + "-" + pad(m + 1) + "-" + pad(d);
  const nthWeekday = (year, month, weekday, n) => {   // e.g. 4th Thursday
    const first = new Date(year, month, 1).getDay();
    return 1 + ((weekday - first + 7) % 7) + (n - 1) * 7;
  };
  const M = WOTD.MOVING;
  const holiday = (key, i) => ({ word: M[key].words[i % M[key].words.length], label: M[key].name, kind: "holiday" });

  // Holiday words rotate year to year, starting with the first word in the list.
  if (M.lunarNewYear.dates.includes(iso)) return holiday("lunarNewYear", y - 2027);
  if (M.midAutumn.dates.includes(iso)) return holiday("midAutumn", y - 2026);
  if (m === 10 && d === nthWeekday(y, 10, 4, 4)) return holiday("thanksgiving", 0);
  if (m === 4 && d === nthWeekday(y, 4, 0, 2)) return holiday("mothersDay", 0);
  if (m === 5 && d === nthWeekday(y, 5, 0, 3)) return holiday("fathersDay", 0);

  const dayOfYear = Math.floor((date - new Date(y, 0, 0)) / 86400000);
  for (const key of ["birthday", "swim", "soccer", "basketball", "dentist", "doctor"]) {
    if ((activities || []).includes(key)) {
      const set = WOTD.ACTIVITY[key];
      return { word: set.words[dayOfYear % set.words.length], label: set.label, kind: "activity" };
    }
  }
  return { word: WOTD.MONTHS[m][d - 1], label: "Word of the day", kind: "day" };
};
