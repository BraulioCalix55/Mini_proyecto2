# -*- coding: utf-8 -*-
"""mini_proyecto2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eWFtp73WpvSWJ-2x-sMX9Dy0Sb2hamR_
"""

from google.colab import drive
drive.mount("/content/drive")

"""Parte del codigo de entrenamiento en el codigo de programamos en vs code sacamos el valor del mean y del std, pero el codigo que realmente hizo la diferencia es el codigo que está aquí"""

# Commented out IPython magic to ensure Python compatibility.
import torchvision
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn as nn
import torch.optim as optim
import PIL.Image as Image
import sys
import os
import json
"""
este codigo se corrio en google colab ya que la computadora de ninguno de los miemrbos tiene la 
capacidad suficiente como para poder procesarla
eso si, se podría decir que hasta cierto punto abusamos ya que llegamos al punto de que nos querian cobrar
10$ por el servicio, entonces hasta ahi llego la sesión de entrenamientos xD
"""

#para poder probar el codigo va a tener que poner el nos dos path de abajo los directorios que vaya a usar para las pruebas corrspondientes
train_dataset_path = '/content/drive/MyDrive/training_set'
test_dataset_path = '/content/drive/MyDrive/CHURROS_P'

mean= [0.4806, 0.4035, 0.3287]
std=[0.2387, 0.2181, 0.2101]


#la imagen de entrenamiento se tiene que transformar un poco para que se pueda entreanr bien el pytorch
train_transforms = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize(torch.Tensor(mean), torch.Tensor(std))
])
#estas son las imagenes de prueba, igual se ocupa modificar, pero no tanto, solo normalizar
test_transforms = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize(torch.Tensor(mean), torch.Tensor(std))
])
#ruta del folder train
train_dataset = torchvision.datasets.ImageFolder(
    root=train_dataset_path, transform=train_transforms
)
#ruta del folder test
test_dataset = torchvision.datasets.ImageFolder(
    root=train_dataset_path, transform=test_transforms
)
#data load de ambos folders
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=False)

#se define el dispositivo que se va a usar  
def set_device():
    if torch.cuda.is_available():
        dev = "cuda:0"
    else:
        dev = "cpu"
    return torch.device(dev)

#metodo para entrenar 
def train_nn(model, train_loader, test_loader, criterion, optimizer, n_epochs):
    device = set_device()
    best_acc = 0
    #se guarda el best_acc para guardar el mejor modelo posible
    #para cada epoch o iteracion por asi decirlo, se inizializan todas las variables necesaras
    for epoch in range(n_epochs):
        print("Epoch number %d" % (epoch + 1))
        model.train()
        running_loss = 0.0
        running_correct = 0.0
        total = 0
        # prepara la imagen correspondiente para poder hacerle un predict
        for data in train_loader:
            images, labels = data
            images = images.to(device)
            labels = labels.to(device)
            total += labels.size(0)

            optimizer.zero_grad()

            outputs = model(images)
            #realiza el predict
            _, predicted = torch.max(outputs.data, 1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            running_correct += (labels == predicted).sum().item()

        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100.00 * running_correct / total
        #imprime los valores de la iteracion correspondiente en el training
        print("-Training dataset. got %d out of %d images correctly (%.3f%%). Epoch loss: %.3f"
               % (running_correct, total, epoch_acc, epoch_loss))

        test_dataset_acc = evaluate_model_on_test_set(model, test_loader)
        #va viendo que modelo es mejor en base al acc asi se ve cual se va a guardar
        if test_dataset_acc > best_acc:
            best_acc = test_dataset_acc
            save_checkpoint(model, epoch,optimizer,best_acc)

    
    return model

  #guarda el mejor modelo 
def save_checkpoint(model, epoch,optimizer,best_acc):
    state = {
        'epoch': epoch +1,
        'model': model.state_dict(),
        'best accuracy': best_acc
    }
    torch.save(state,'model_best_checkpoint.pth.tar')
  #hace pruebas con el testing data set
def evaluate_model_on_test_set(model, test_loader):
    model.eval()
    predicted_correctly_on_epoch = 0
    total = 0
    device = set_device()

    with torch.no_grad():
        for data in test_loader:
            images, labels = data
            images = images.to(device)
            labels = labels.to(device)
            total += labels.size(0)

            outputs = model(images)

            _, predicted = torch.max(outputs.data, 1)

            predicted_correctly_on_epoch += (predicted == labels).sum().item()

    epoch_acc = 100.0 * predicted_correctly_on_epoch / total
    print("-Testing dataset. Got %d out of %d images correctly (%.3f%%)"
         % (predicted_correctly_on_epoch, total, epoch_acc))
    return epoch_acc


resnet18_model = models.resnet18(pretrained=True)
num_ftrs = resnet18_model.fc.in_features
#tenemos 34 marcas, entonces son 34 clases que tenemos
number_of_classes = 34
resnet18_model.fc = nn.Linear(num_ftrs, number_of_classes)
device = set_device()
resnet_18_model = resnet18_model.to(device)
loss_fn = nn.CrossEntropyLoss()

optimizer = optim.SGD(resnet18_model.parameters(), lr=0.01, momentum=0.9, weight_decay=0.003)
#se entrena 
train_nn(resnet18_model, train_loader, test_loader, loss_fn, optimizer, 20)

#carga el modelo que se guardo como el mejor
checkpoint = torch.load('/content/model_best_checkpoint.pth.tar')

resnet18_model = models.resnet18()
num_ftrs = resnet18_model.fc.in_features
number_of_classes = 34
resnet18_model.fc = nn.Linear(num_ftrs, number_of_classes)
resnet_18_model = resnet18_model.to(device)
resnet18_model.load_state_dict(checkpoint['model'])
torch.save(resnet18_model,'best_model.pth')



#ruta = sys.argv[1]
#destino=sys.argv[2]
#se reordenaron las fotos de los churros a solo marcas, esto ya que la primera vez  que intentamos pues se fue asi
#y despues volver a acomodar las fotos pues se hacia muy engorroso, asi que el reconocimiento es a nivel de marca 
#no de marca/sabor como se queria en un inicio
#abajo de todo el codigo que si funciona se encuentra un codigo que no funciona, ese fue otro aproach que intentamos 
#el cual no sirvio para nada, ya que hacia una cosa completamente distinta


#se ocupa que las clases esten en el mismo orden que en lacarpeta 
classes=["anillitos","bue_nachos","cappy","caribas","centavitos","cheetos","chips","churritos","crujitos","del_rancho_chicharrones","del_rancho_rosquillas_criollas","doraditas",
    "doritos","elotitos","fiesta_snax","frijoli","frit-os","jalapenos","lays","maiz_chino", "nachos","palitos","pop","quesi_trix","ranchitas","rica_sula_tajaditas","taco","takis","taqueritos",
    "toztecas","yucatekas","yummix","zambos","zibas"]
    
#estos datos se sacan en la clases mean_std, pero solo se ocupan una vez
mean= [0.4806, 0.4035, 0.3287]
std=[0.2387, 0.2181, 0.2101]
#transformaciones necesarias
image_transforms = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize(torch.Tensor(mean), torch.Tensor(std))
])

#hace la clasificacion
def Clasificar(model, image_transforms, image_path, classes):
    model.eval()
    image = Image.open(image_path)
    image = image_transforms(image).cuda()
    #se pasa la imagen al modelo
    image = image.unsqueeze(0)
    output = model(image)
    _, prediction = torch.max(output.data, 1)
    return classes[prediction.item()]


def ActualizaDirectorio(i, marca):
    dictionary.update({i: {
        "marca": marca
    }})

#escritura de jason, cada que se corre se escribe de nuevo, se puede hacer append si se cambia el w por a
def CreaJson():
    json_obj = json.dumps(dictionary, indent=4)
    with open("/content/predictions.json", "w") as outfile:
        outfile.write(json_obj)
#se generara el codigo json correspondiente para poder leerlo despues

#python mp2_04_evaluar_clasificador.py [path de directorio para probar] [path del modelo] [Json de salida]

def main():
    
    for i in os.listdir(directory):
        marca = Clasificar(model, image_transforms, directory+i, classes)
        ActualizaDirectorio(i, marca)
    CreaJson()

#menu de inputs al correr
#hay que cambiar los paths del directorio y del modelo, a no ser que decida usar estos mismos valores, no creemos, por lo tanto usted cambie esos paths
if __name__ == '__main__':
    directory = "/content/drive/MyDrive/CHURROS_P/"
    model_path = "/content/best_model.pth"
    model = torch.load(model_path)
    dictionary = {}
    main()